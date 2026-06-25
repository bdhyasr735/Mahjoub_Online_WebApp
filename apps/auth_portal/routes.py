# coding: utf-8
# 📂 apps/auth_portal/routes.py - النسخة النهائية المباشرة

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from apps.models.admin_db import AdminUser

# إنشاء Blueprint للـ Auth Portal
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

# المسار الديناميكي (يقرأ من متغيرات البيئة أو يستخدم القيمة الافتراضية)
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم في قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        # التحقق من كلمة المرور
        if admin and admin.check_password(password):
            # تسجيل الدخول مباشرة
            login_user(admin) 
            flash('تم تسجيل الدخول بنجاح!', 'success')
            
            # توجيه إلى لوحة التحكم (تم تصحيح المسار ليكون dashboard)
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('auth/login.html')

# مسار تسجيل الخروج (إضافي للأمان)
@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('auth_portal.login'))
