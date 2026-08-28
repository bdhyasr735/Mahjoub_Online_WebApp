"""
apps/suppliers_auth_portal/routes.py
مسارات بوابة مصادقة وإدارة الموردين والموظفين
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from .auth_service import auth_service

suppliers_bp = Blueprint(
    'suppliers_auth_portal',
    __name__,
    url_prefix='/supplier',
    template_folder='templates',
    static_folder='static'
)

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للموردين أو الموظفين"""
    if request.method == 'GET':
        # التحقق مما إذا كان الطلب قادماً من متصفح (يريد صفحة HTML) أو طلب API برْمجي
        if 'text/html' in request.headers.get('Accept', ''):
            return render_template('suppliers_auth_portal/login.html')
        return jsonify({
            "status": "success",
            "message": "مرحباً بك في بوابة تسجيل الدخول للموردين",
            "csrf_token": auth_service.generate_csrf_token()
        })

    data = request.get_json() if request.is_json else request.form
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "")
    user_type = data.get("user_type", "supplier")

    if not identifier or not password:
        return jsonify({"success": False, "message": "الرجاء إدخال البريد الإلكتروني أو رقم الجوال وكلمة المرور"}), 400

    success, message, result = auth_service.authenticate(identifier, password, user_type)
    
    if not success:
        return jsonify({"success": False, "message": message}), 401

    # حفظ الجلسة
    session['user_id'] = result.get('supplier', {}).get('id') or result.get('employee', {}).get('id')
    session['user_type'] = result.get('user_type')
    
    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 200


@suppliers_bp.route('/register-page', methods=['GET'])
def register_page():
    """عرض صفحة إنشاء حساب مورد جديد (HTML)"""
    return render_template('suppliers_auth_portal/register.html')


@suppliers_bp.route('/register', methods=['POST'])
def register():
    """مسار تسجيل مورد جديد وإنشاء المحفظة المالية"""
    data = request.get_json() if request.is_json else request.form
    success, message, result = auth_service.register_supplier(data)
    
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 201


@suppliers_bp.route('/forgot-password-page', methods=['GET'])
def forgot_password_page():
    """عرض صفحة استعادة كلمة المرور (HTML) - تم إضافتها لحل خطأ الـ BuildError"""
    return render_template('suppliers_auth_portal/forgot_password.html')


@suppliers_bp.route('/verify-page', methods=['GET'])
def verify_page():
    """عرض صفحة التحقق من الرمز OTP (HTML)"""
    return render_template('suppliers_auth_portal/verify.html')


@suppliers_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """طلب رمز التحقق لاستعادة كلمة المرور (API)"""
    data = request.get_json() if request.is_json else request.form
    identifier = data.get("identifier", "")
    
    success, message, result = auth_service.initiate_forgot_password(identifier)
    if not success:
        return jsonify({"success": False, "message": message}), 404

    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 200


@suppliers_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور باستخدام رمز التحقق (OTP)"""
    data = request.get_json() if request.is_json else request.form
    identifier = data.get("identifier", "")
    otp_code = data.get("otp_code", "")
    new_password = data.get("new_password", "")

    success, message = auth_service.verify_otp_and_reset_password(identifier, otp_code, new_password)
    if not success:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({
        "success": True,
        "message": message
    }), 200


@suppliers_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """تسجيل الخروج وإنهاء الجلسة"""
    session.clear()
    if request.method == 'GET' or 'text/html' in request.headers.get('Accept', ''):
        return redirect(url_for('suppliers_auth_portal.login'))
    return jsonify({"success": True, "message": "تم تسجيل الخروج بنجاح"})
