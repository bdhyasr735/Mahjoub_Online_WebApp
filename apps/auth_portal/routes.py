# coding: utf-8
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.admin_db import AdminUser

# تعريف الـ Blueprint الخاص ببوابة الإدارة
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates'
)

# الرابط السري للإدارة
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    """
    بوابة دخول الإدارة حصراً.
    تخزن نوع المستخدم في الجلسة لضمان الفصل التام.
    """
    if current_user.is_authenticated and session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث في جدول المسؤولين فقط
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin, remember=True)
            # تحديد نوع الجلسة كإدارة لمنع التداخل مع الموردين
            session['user_type'] = 'admin' 
            
            flash('مرحباً بك يا مدير النظام.', 'success')
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            flash('بيانات دخول غير صحيحة.', 'danger')
            
    return render_template('auth/login.html')

@auth_portal.route('/logout')
def logout():
    """
    تسجيل الخروج مع مسح شامل للجلسة لمنع أي تداخل في الصلاحيات.
    تمت إزالة @login_required لضمان التنفيذ في جميع الحالات.
    """
    # تسجيل الخروج من Flask-Login
    logout_user()
    # مسح الجلسة بالكامل لضمان عدم بقاء أي أثر لـ user_type أو غيره
    session.clear() 
    
    # التوجيه لبوابة دخول الإدارة
    return redirect(url_for('auth_portal.login'))
