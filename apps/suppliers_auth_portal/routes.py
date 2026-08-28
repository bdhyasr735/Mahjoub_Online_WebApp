"""
apps/suppliers_auth_portal/routes.py
مسارات بوابة مصادقة وإدارة الموردين والموظفين
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, g
from .auth_service import auth_service
from .seo_service import seo_service

suppliers_bp = Blueprint(
    'suppliers_bp',  # ← تغيير: يجب أن يتطابق مع الاسم في apps/__init__.py
    __name__,
    url_prefix='/suppliers',  # ← تغيير: من /supplier إلى /suppliers
    template_folder='templates',
    static_folder='static'
)


# ==================== قبل كل طلب ====================
@suppliers_bp.before_request
def before_request():
    """توليد CSRF token وإضافته إلى السياق العالمي للقوالب"""
    if 'csrf_token' not in session:
        session['csrf_token'] = auth_service.generate_csrf_token()
    g.csrf_token = session['csrf_token']


# ==================== تسجيل الدخول ====================
@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للموردين أو الموظفين"""
    if request.method == 'GET':
        # التحقق مما إذا كان الطلب قادماً من متصفح (يريد صفحة HTML) أو طلب API برْمجي
        if 'text/html' in request.headers.get('Accept', ''):
            # تمرير CSRF token إلى القالب
            return render_template(
                'suppliers_auth_portal/login.html',
                csrf_token=session.get('csrf_token', auth_service.generate_csrf_token())
            )
        return jsonify({
            "status": "success",
            "message": "مرحباً بك في بوابة تسجيل الدخول للموردين",
            "csrf_token": auth_service.generate_csrf_token()
        })

    data = request.get_json() if request.is_json else request.form
    
    # دعم مرن لاستقبال المعرف من أي حقل محتمل (identifier, username, email, phone)
    identifier = (
        data.get("identifier") or 
        data.get("username") or 
        data.get("email") or 
        data.get("phone", "")
    ).strip()
    
    password = data.get("password", "")
    user_type = data.get("user_type", "supplier")

    if not identifier or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور"}), 400

    # التحقق من CSRF للطلبات غير GET
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403

    success, message, result = auth_service.authenticate(identifier, password, user_type)
    
    if not success:
        return jsonify({"success": False, "message": message}), 401

    # حفظ الجلسة
    session['user_id'] = result.get('supplier', {}).get('id') or result.get('employee', {}).get('id')
    session['user_type'] = result.get('user_type')
    session['supplier_id'] = result.get('supplier', {}).get('id')
    
    return jsonify({
        "success": True,
        "message": message,
        "data": result,
        "redirect_url": "/suppliers/dashboard"  # ← تغيير: من /supplier إلى /suppliers
    }), 200


# ==================== عرض صفحة التسجيل ====================
@suppliers_bp.route('/register-page', methods=['GET'])
def register_page():
    """عرض صفحة إنشاء حساب مورد جديد (HTML)"""
    return render_template(
        'suppliers_auth_portal/register.html',
        csrf_token=session.get('csrf_token', auth_service.generate_csrf_token())
    )


# ==================== تسجيل مورد جديد ====================
@suppliers_bp.route('/register', methods=['POST'])
def register():
    """مسار تسجيل مورد جديد وإنشاء المحفظة المالية"""
    data = request.get_json() if request.is_json else request.form
    
    # التحقق من CSRF
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    success, message, result = auth_service.register_supplier(data)
    
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "data": result,
        "redirect_url": "/suppliers/login"  # ← تغيير: من /supplier إلى /suppliers
    }), 201


# ==================== صفحة استعادة كلمة المرور ====================
@suppliers_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور (HTML)"""
    return render_template(
        'suppliers_auth_portal/forgot_password.html',
        csrf_token=session.get('csrf_token', auth_service.generate_csrf_token())
    )


# ==================== طلب OTP لاستعادة كلمة المرور ====================
@suppliers_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """طلب رمز التحقق لاستعادة كلمة المرور"""
    data = request.get_json() if request.is_json else request.form
    
    # التحقق من CSRF
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    identifier = (
        data.get("identifier") or 
        data.get("username") or 
        data.get("email") or 
        data.get("phone", "")
    ).strip()
    
    if not identifier:
        return jsonify({"success": False, "message": "يرجى إدخال البريد الإلكتروني أو رقم الجوال"}), 400
    
    success, message, result = auth_service.initiate_forgot_password(identifier)
    if not success:
        return jsonify({"success": False, "message": message}), 404

    # تخزين المعرف في الجلسة للاستخدام في reset-password
    session['reset_identifier'] = identifier

    return jsonify({
        "success": True,
        "message": message,
        "otp_sent": True,
        "data": result
    }), 200


# ==================== إعادة إرسال OTP ====================
@suppliers_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """إعادة إرسال رمز التحقق"""
    data = request.get_json() if request.is_json else request.form
    
    # التحقق من CSRF
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    # استرجاع المعرف من الجلسة أو من الطلب
    identifier = data.get("identifier") or session.get('reset_identifier')
    
    if not identifier:
        return jsonify({"success": False, "message": "لم يتم العثور على طلب سابق لإعادة التعيين"}), 400
    
    success, message, result = auth_service.initiate_forgot_password(identifier)
    if not success:
        return jsonify({"success": False, "message": message}), 404
    
    return jsonify({
        "success": True,
        "message": "تم إعادة إرسال رمز التحقق بنجاح",
        "data": result
    }), 200


# ==================== إعادة تعيين كلمة المرور ====================
@suppliers_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور باستخدام رمز التحقق (OTP)"""
    data = request.get_json() if request.is_json else request.form
    
    # التحقق من CSRF
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    identifier = (
        data.get("identifier") or 
        session.get('reset_identifier') or
        data.get("username") or 
        data.get("email") or 
        data.get("phone", "")
    ).strip()
    
    otp_code = data.get("otp_code", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not identifier:
        return jsonify({"success": False, "message": "المعرف مطلوب"}), 400
    
    if not otp_code:
        return jsonify({"success": False, "message": "رمز التحقق مطلوب"}), 400
    
    if not new_password:
        return jsonify({"success": False, "message": "كلمة المرور الجديدة مطلوبة"}), 400
    
    if new_password != confirm_password:
        return jsonify({"success": False, "message": "كلمتا المرور غير متطابقتين"}), 400

    success, message = auth_service.verify_otp_and_reset_password(identifier, otp_code, new_password)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    # مسح بيانات الجلسة بعد النجاح
    session.pop('reset_identifier', None)

    return jsonify({
        "success": True,
        "message": message,
        "redirect_url": "/suppliers/login"  # ← تغيير: من /supplier إلى /suppliers
    }), 200


# ==================== صفحة التحقق من الحساب ====================
@suppliers_bp.route('/verify-page', methods=['GET'])
def verify_page():
    """عرض صفحة التحقق من الرمز OTP (HTML)"""
    return render_template(
        'suppliers_auth_portal/verify.html',
        csrf_token=session.get('csrf_token', auth_service.generate_csrf_token())
    )


# ==================== التحقق من OTP (POST) ====================
@suppliers_bp.route('/verify', methods=['POST'])
def verify_otp():
    """التحقق من رمز OTP لتأكيد الحساب"""
    data = request.get_json() if request.is_json else request.form
    
    # التحقق من CSRF
    if not auth_service.validate_csrf_token(data.get("csrf_token")):
        return jsonify({"success": False, "message": "طلب غير مصرح به (CSRF)"}), 403
    
    otp_code = data.get("otp_code", "").strip()
    
    if not otp_code or len(otp_code) < 4:
        return jsonify({"success": False, "message": "يرجى إدخال رمز التحقق بشكل صحيح"}), 400
    
    return jsonify({
        "success": True,
        "message": "تم التحقق من الحساب بنجاح",
        "redirect_url": "/suppliers/login"  # ← تغيير: من /supplier إلى /suppliers
    }), 200


# ==================== تسجيل الخروج ====================
@suppliers_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """تسجيل الخروج وإنهاء الجلسة"""
    session.clear()
    if request.method == 'GET' or 'text/html' in request.headers.get('Accept', ''):
        return redirect(url_for('suppliers_bp.login'))  # ← تغيير
    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح"}), 200


# ==================== لوحة التحكم (مؤقت) ====================
@suppliers_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة تحكم المورد (مؤقتة لعرضها بعد تسجيل الدخول)"""
    if 'user_id' not in session:
        return redirect(url_for('suppliers_bp.login'))  # ← تغيير
    
    return jsonify({
        "message": "مرحباً بك في لوحة التحكم",
        "user_id": session.get('user_id'),
        "user_type": session.get('user_type')
    })


# ==================== مسارات SEO ====================
@suppliers_bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """خريطة الموقع للمحركات البحث"""
    from .seo_service import generate_sitemap_xml
    return generate_sitemap_xml(), 200, {'Content-Type': 'application/xml'}


@suppliers_bp.route('/robots.txt', methods=['GET'])
def robots():
    """ملف تعليمات محركات البحث"""
    from .seo_service import generate_robots_txt
    return generate_robots_txt(), 200, {'Content-Type': 'text/plain'}
