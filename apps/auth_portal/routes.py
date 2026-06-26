# coding: utf-8
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.admin_db import AdminUser

# [التنظيم السيادي]: تعريف الـ Blueprint
# نستخدم اسم 'auth_portal' ليكون هو المعرف داخل التطبيق
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates',
    url_prefix='/auth'
)

# [صمام الخصوصية]: مسار الدخول
# الرابط سيكون دائماً: /auth/m7jb_sovereign_hq_v2_99x
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    # منع إعادة الدخول للمسؤولين المتصلين بالفعل
    if current_user.is_authenticated:
        # تأكد من أن 'admin_dashboard.dashboard' هو اسم الـ Blueprint المعتمد في نظامك
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            # البحث عن المسؤول
            admin = AdminUser.query.filter_by(username=username).first()
            
            # التحقق الأمني (PBKDF2)
            if admin and admin.check_password(password):
                login_user(admin, remember=True)
                flash('تم تسجيل الدخول بنجاح!', 'success')
                
                # التوجيه إلى لوحة الإدارة
                return redirect(url_for('admin_dashboard.dashboard'))
            else:
                flash('بيانات الدخول غير صحيحة.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Login process error: {str(e)}")
            flash('حدث خطأ فني أثناء المعالجة.', 'danger')
            
    # تأكد من أن الملف موجود في: apps/auth_portal/templates/auth/login.html
    return render_template('auth/login.html')

@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('auth_portal.login'))
