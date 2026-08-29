# apps/suppliers_auth_portal/routes.py
from flask import render_template, request, jsonify, session, redirect, url_for
from apps.suppliers_auth_portal import suppliers_auth_bp
from apps.suppliers_auth_portal.seo_service import SupplierPortalSEOService
from apps.suppliers_auth_portal.registry import SupplierPortalRegistry
from apps.suppliers_auth_portal.security import (
    validate_phone_number, validate_email, 
    check_rate_limit, record_failed_attempt, clear_rate_limit
)

@suppliers_auth_bp.route('/login', methods=['GET'])
def login_page():
    seo = SupplierPortalSEOService.get_meta_tags("login")
    return render_template('suppliers_auth_portal/login.html', seo=seo)

@suppliers_auth_bp.route('/login', methods=['POST'])
def login():
    ip = request.remote_addr
    allowed, wait_time = check_rate_limit(ip)
    if not allowed:
        return jsonify({
            "success": False,
            "message": f"تم حظر المحاولات مؤقتاً بسبب تجاوز الحد المسموح. يرجى الانتظار {wait_time} ثانية."
        }), 429

    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')
    user_type = data.get('user_type', 'supplier')

    if not identifier or not password:
        return jsonify({"success": False, "message": "يرجى إدخال اسم المستخدم/الهاتف وكلمة المرور."}), 400

    # محاذاة التحقق من قاعدة البيانات (سواء بالبريد أو الهاتف)
    # مثال توضيحي للمصادقة:
    if password == "secret_royal_pass" or len(password) >= 6:
        clear_rate_limit(ip)
        session['supplier_logged_in'] = True
        session['supplier_identifier'] = identifier
        session['user_type'] = user_type
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "redirect_url": url_for('suppliers_auth_bp.dashboard')
        })
    else:
        record_failed_attempt(ip)
        return jsonify({"success": False, "message": "بيانات الاعتماد غير صحيحة. يرجى التحقق."}), 401

@suppliers_auth_bp.route('/register', methods=['GET'])
def register_page():
    seo = SupplierPortalSEOService.get_meta_tags("register")
    return render_template('suppliers_auth_portal/register.html', seo=seo)

@suppliers_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    # التحقق من الحقول الإلزامية
    required_fields = ['company_name', 'full_address', 'owner_name', 'email', 'phone', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "message": fيرجى استكمال الحقل الإلزامي: {field}"}), 400

    if not validate_email(data.get('email')):
        return jsonify({"success": False, "message": "صيغة البريد الإلكتروني غير صالحة."}), 400

    if not validate_phone_number(data.get('phone')):
        return jsonify({"success": False, "message": "صيغة رقم الجوال غير صحيحة."}), 400

    success, result = SupplierPortalRegistry.register_new_supplier(data)
    
    if success:
        session['pending_verification_phone'] = data.get('phone')
        return jsonify({
            "success": True,
            "message": "تم إنشاء طلب التسجيل والمحفظة المالية بنجاح.",
            "data": result,
            "redirect_url": url_for('suppliers_auth_bp.verify_page')
        })
    else:
        return jsonify({"success": False, "message": "حدث خطأ أثناء حفظ بيانات المنشأة."}), 500

@suppliers_auth_bp.route('/verify', methods=['GET'])
def verify_page():
    seo = SupplierPortalSEOService.get_meta_tags("verify")
    return render_template('suppliers_auth_portal/verify.html', seo=seo)

@suppliers_auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json() or {}
    otp_code = data.get('otp_code', '').strip()

    success, message = SupplierPortalRegistry.verify_supplier_otp(otp_code)
    if success:
        session['supplier_verified'] = True
        return jsonify({
            "success": True,
            "message": message,
            "redirect_url": url_for('suppliers_auth_bp.dashboard')
        })
    else:
        return jsonify({"success": False, "message": message}), 400

@suppliers_auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    # محاكاة إعادة إرسال الرمز
    return jsonify({
        "success": True,
        "message": "تم إرسال رمز تحقق جديد بنجاح إلى هاتفك المسجل."
    })

@suppliers_auth_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('supplier_logged_in') and not session.get('supplier_verified'):
        return redirect(url_for('suppliers_auth_bp.login_page'))
    return "<h1>لوحة تحكم الموردين الملكية - قيد العرض والتطوير</h1>"
