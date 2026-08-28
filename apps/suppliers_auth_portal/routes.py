"""
apps/suppliers_auth_portal/routes.py
مسارات ونقاط نهاية بوابة الموردين وموظفيهم (Flask / Django Blueprint & API)
"""

import json
from functools import wraps
from typing import Callable, Any

try:
    from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, Response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    # محاكاة كائن Blueprint في حال استخدام البيئة كـ Framework مستقل
    class Blueprint:
        def __init__(self, name, import_name, template_folder=None, url_prefix=None):
            self.name = name
            self.url_prefix = url_prefix
            self.routes = {}

        def route(self, rule, methods=None):
            def decorator(f):
                self.routes[rule] = {"func": f, "methods": methods or ["GET"]}
                return f
            return decorator

from .auth_service import auth_service
from .registry import SECURITY_CONFIG, EMPLOYEE_ROLES, SEO_CONFIG
from .seo_service import seo_service, generate_sitemap_xml, generate_robots_txt

# تعريف مسار الموديول مع مطابقة اسم الـ Blueprint المطلوب في النظام الرئيسي والقوالب
suppliers_bp = Blueprint(
    "suppliers_auth_portal",
    __name__,
    template_folder="templates",
    url_prefix="/supplier"
)

def require_csrf(f: Callable) -> Callable:
    """متحقق حماية CSRF لطلبات الـ POST / PUT / DELETE عبر X-CSRFToken أو X-CSRF-Token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not HAS_FLASK:
            return f(*args, **kwargs)

        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            token = (
                request.headers.get("X-CSRFToken") or
                request.headers.get("X-CSRF-Token") or
                request.headers.get("x-csrftoken") or
                request.headers.get("x-csrf-token") or
                (request.form.get("csrf_token") if request.form else None)
            )

            if not auth_service.validate_csrf_token(token):
                return jsonify({
                    "success": False,
                    "error": "csrf_verification_failed",
                    "message": "فشل التحقق الأمني من الـ CSRF Token. يرجى إعادة تحميل الصفحة."
                }), 403

        return f(*args, **kwargs)
    return decorated_function


# ==================== 1. مسار تسجيل الدخول (login) ====================
@suppliers_bp.route("/login", methods=["GET", "POST"])
@require_csrf
def login():
    """عرض صفحة الدخول أو معالجة طلب تسجيل دخول المورد / الموظف"""
    if HAS_FLASK and request.method == "GET":
        csrf_token = auth_service.generate_csrf_token()
        seo_data = seo_service.get_page_metadata("login")
        return render_template(
            "suppliers_auth_portal/login.html",
            csrf_token=csrf_token,
            page_title=seo_data["title"],
            seo=seo_data
        )

    # معالجة طلب POST
    data = (request.get_json(silent=True) or request.form.to_dict()) if HAS_FLASK else {}
    identifier = data.get("identifier", "")
    password = data.get("password", "")
    user_type = data.get("user_type", "supplier")  # 'supplier' أو 'employee'

    success, message, result = auth_service.authenticate(identifier, password, user_type)
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "redirect_url": "/supplier/dashboard",
            "data": result
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 401


# ==================== 2. مسار اشتراك الموردين الجدد (register) ====================
@suppliers_bp.route("/register", methods=["GET", "POST"])
@require_csrf
def register():
    """
    تسجيل مورد جديد، إنشاء المحفظة المالية المرتبطة تلقائياً،
    وإدارة موظفي الموردين المرفقين بالطلب.
    """
    if HAS_FLASK and request.method == "GET":
        csrf_token = auth_service.generate_csrf_token()
        seo_data = seo_service.get_page_metadata("register")
        return render_template(
            "suppliers_auth_portal/register.html",
            csrf_token=csrf_token,
            employee_roles=EMPLOYEE_ROLES,
            page_title=seo_data["title"],
            seo=seo_data
        )

    # معالجة طلب POST للتسجيل
    data = (request.get_json(silent=True) or request.form.to_dict()) if HAS_FLASK else {}
    
    # دعم موظفي المورد المرفقين في نموذج الاشتراك
    if isinstance(data.get("employees"), str):
        try:
            data["employees"] = json.loads(data["employees"])
        except Exception:
            data["employees"] = []

    success, message, result = auth_service.register_supplier(data)
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "redirect_url": "/supplier/login?registered=1",
            "data": result
        }), 201
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400


# ==================== 3. مسار استعادة كلمة المرور (forgot_password) ====================
@suppliers_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    """عرض قالب استعادة وتحديث كلمة المرور على مرحلتين"""
    csrf_token = auth_service.generate_csrf_token()
    if HAS_FLASK:
        return render_template(
            "suppliers_auth_portal/forgot_password.html",
            csrf_token=csrf_token,
            page_title="استعادة كلمة المرور"
        )
    return jsonify({"csrf_token": csrf_token})


@suppliers_bp.route("/forgot-password/request-otp", methods=["POST"])
@require_csrf
def request_password_reset_otp():
    """
    المرحلة الأولى: التحقق من المستخدم وإرسال رمز التحقق otp_sent
    """
    data = (request.get_json(silent=True) or request.form.to_dict()) if HAS_FLASK else {}
    identifier = data.get("identifier", "").strip()

    if not identifier:
        return jsonify({
            "success": False,
            "message": "يرجى إدخال اسم المستخدم، رقم الهاتف، أو البريد الإلكتروني المسجل"
        }), 400

    success, message, result = auth_service.initiate_forgot_password(identifier)
    if success:
        return jsonify({
            "success": True,
            "otp_sent": True,
            "message": message,
            "data": result
        }), 200
    else:
        return jsonify({
            "success": False,
            "otp_sent": False,
            "message": message
        }), 404


@suppliers_bp.route("/forgot-password/reset", methods=["POST"])
@require_csrf
def reset_password_with_otp():
    """
    المرحلة الثانية: التحقق من الرمز وتحديث كلمة المرور بعد تشفيرها
    """
    data = (request.get_json(silent=True) or request.form.to_dict()) if HAS_FLASK else {}
    identifier = data.get("identifier", "").strip()
    otp_code = data.get("otp_code", "").strip()
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "كلمتا المرور غير متطابقتين"
        }), 400

    success, message = auth_service.verify_otp_and_reset_password(identifier, otp_code, new_password)
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "redirect_url": "/supplier/login?reset_done=1"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400


# ==================== 4. مسار التحقق من الرمز (verify) ====================
@suppliers_bp.route("/verify", methods=["GET", "POST"])
@require_csrf
def verify_account():
    """صفحة والتحقق من كود الـ OTP لحساب المورد أو الموظف"""
    if HAS_FLASK and request.method == "GET":
        csrf_token = auth_service.generate_csrf_token()
        identifier = request.args.get("identifier", "")
        return render_template(
            "suppliers_auth_portal/verify.html",
            csrf_token=csrf_token,
            identifier=identifier,
            page_title="التحقق الأمني من الرمز"
        )

    data = (request.get_json(silent=True) or request.form.to_dict()) if HAS_FLASK else {}
    identifier = data.get("identifier", "")
    otp_code = data.get("otp_code", "")

    # التحقق من صلاحية الرمز
    record = auth_service.otp_store.get(identifier.lower())
    if record and record["otp_code"] == otp_code:
        return jsonify({"success": True, "message": "تم التحقق بنجاح"}), 200
    return jsonify({"success": False, "message": "رمز التحقق غير صحيح أو منتهي الصلاحية"}), 400


# ==================== 5. إدارة موظفي المورد (Employees) ====================
@suppliers_bp.route("/employees", methods=["GET", "POST"])
@require_csrf
def manage_employees():
    """عرض وإضافة موظفي المورد"""
    if HAS_FLASK and request.method == "POST":
        data = request.get_json(silent=True) or request.form.to_dict()
        supplier_id = data.get("supplier_id", "")
        success, message, emp = auth_service.add_employee(supplier_id, data)
        return jsonify({"success": success, "message": message, "employee": emp}), (201 if success else 400)

    supplier_id = request.args.get("supplier_id", "") if HAS_FLASK else ""
    employees = auth_service.get_supplier_employees(supplier_id)
    return jsonify({"success": True, "employees": employees}), 200


# ==================== 6. محفظة المورد المالية (Wallet) ====================
@suppliers_bp.route("/wallet/<supplier_id>", methods=["GET"])
def get_wallet(supplier_id):
    """استرجاع بيانات المحفظة المالية المرتبطة بالمورد"""
    wallet = auth_service.get_supplier_wallet(supplier_id)
    if wallet:
        return jsonify({"success": True, "wallet": wallet}), 200
    return jsonify({"success": False, "message": "المحفظة غير موجودة"}), 404


# ==================== 7. تحسين محركات البحث والظهور (SEO Endpoints) ====================
@suppliers_bp.route("/robots.txt", methods=["GET"])
def get_robots_txt_route():
    """توليد ملف robots.txt لتوجيه عناكب محركات البحث وفق السياسات المعتمدة"""
    content = generate_robots_txt()
    if HAS_FLASK:
        return Response(content, mimetype="text/plain")
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}


@suppliers_bp.route("/sitemap.xml", methods=["GET"])
def get_sitemap_xml_route():
    """توليد خريطة الموقع sitemap.xml لمساعدة عناكب جوجل على فهرسة صفحات الموردين"""
    content = generate_sitemap_xml()
    if HAS_FLASK:
        return Response(content, mimetype="application/xml")
    return content, 200, {"Content-Type": "application/xml; charset=utf-8"}


@suppliers_bp.route("/seo/metadata", methods=["GET"])
def get_seo_metadata():
    """نقطة نهاية API لإرجاع وسوم الميتا وبيانات Schema.org لصفحات الموديول"""
    page = request.args.get("page", "login") if HAS_FLASK else "login"
    metadata = seo_service.get_page_metadata(page)
    return jsonify({"success": True, "page": page, "seo": metadata}), 200
