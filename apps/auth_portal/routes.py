# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff

auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

# المسار السيادي السري الحقيقي لتسجيل الدخول
SECRET_ADMIN_PATH = '/m7jb_sovereign_hq_v2_99x'

@auth_portal.route(SECRET_ADMIN_PATH, methods=['GET', 'POST'])
def secure_admin_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # دعم استقبال البيانات سواء كانت JSON أو Form Data لتجنب أي خطأ
    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    password = data.get('password')
    step = data.get('step', 'credentials')
    otp_code = data.get('otp_code')
    
    if step == 'credentials':
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "يرجى إدخال اسم المستخدم وكلمة المرور."
            }), 400

        # البحث في جدول المديرين الأساسيين أو الموظفين
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            admin = AdminStaff.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            if not admin.is_active:
                return jsonify({
                    "status": "error",
                    "message": "هذا الحساب معطل حالياً."
                }), 403

            session['pre_auth_admin'] = username
            return jsonify({
                "status": "require_otp",
                "message": "تم التحقق من بيانات الدخول بنجاح. يرجى إدخال رمز التحقق السيادي (OTP)."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "بيانات الدخول الإدارية غير صحيحة."
            }), 401

    elif step == 'verify_otp':
        if 'pre_auth_admin' not in session:
            return jsonify({
                "status": "error",
                "message": "جلسة غير صالحة، يرجى إعادة المحاولة."
            }), 400
            
        # يمكنك لاحقاً ربط التحقق من OTP بقاعدة البيانات أو إبقائه مؤقتاً
        if otp_code == "123456":
            auth_username = session.pop('pre_auth_admin', None)
            session['admin_logged_in'] = True
            session['admin_user'] = auth_username
            
            return jsonify({
                "status": "success",
                "message": "تم المصادقة بنجاح، جاري التوجيه...",
                "redirect": url_for('auth_portal.dashboard')
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "رمز التحقق السيادي (OTP) غير صحيح."
            }), 400

    return jsonify({
        "status": "error",
        "message": "طلب غير صالح."
    }), 400


# مسار تمويهي (يظهر للمتطفلين كأن الصفحة غير موجودة)
@auth_portal.route('/login', methods=['GET', 'POST'])
def fake_login():
    abort(404)


@auth_portal.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('auth_portal.secure_admin_login'))
    
    return "مرحباً بك في لوحة التحكم السيادية للإدارة - محجوب أونلاين"
