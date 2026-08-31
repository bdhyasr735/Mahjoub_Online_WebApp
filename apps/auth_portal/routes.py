# -*- coding: utf-8 -*-
# 📂 apps/auth_portal/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff

# توحيد اسم البلتبرنت ليتطابق مع آلية التسجيل التلقائي في التطبيق
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')
auth_portal_bp = auth_portal  # توافقية تامة مع الاستيراد في __init__.py

# المسار السيادي السري الحقيقي لتسجيل الدخول
SECRET_ADMIN_PATH = '/m7jb_sovereign_hq_v2_99x'

@auth_portal.route(SECRET_ADMIN_PATH, methods=['GET', 'POST'])
def secure_admin_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # دعم استقبال البيانات سواء كانت JSON أو Form Data
    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    password = data.get('password')
    
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

        # تسجيل الدخول مباشرة بدون OTP وتفعيل جلسة Admin
        session['admin_logged_in'] = True
        session['user_type'] = 'admin'
        session['_user_id'] = str(admin.id)
        
        return jsonify({
            "status": "success",
            "message": "تم المصادقة بنجاح، جاري التوجيه...",
            "redirect": url_for('auth_portal.dashboard')
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "بيانات الدخول الإدارية غير صحيحة."
        }), 401


# مسار تمويهي (يظهر للمتطفلين كأن الصفحة غير موجودة)
@auth_portal.route('/login', methods=['GET', 'POST'])
def fake_login():
    abort(404)


@auth_portal.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in') and not session.get('_user_id'):
        return redirect(SECRET_ADMIN_PATH)
    
    return "مرحباً بك في لوحة التحكم السيادية للإدارة - محجوب أونلاين"
