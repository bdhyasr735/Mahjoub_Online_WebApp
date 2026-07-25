# coding: utf-8
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from werkzeug.routing import BuildError
from apps.models.admin_db import AdminUser
from apps.models.admin_staff_db import AdminStaff

# تعريف الـ Blueprint
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates'
)

# الرابط السري للإدارة من المتغيرات البيئية
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

def get_admin_dashboard_url():
    """دالة ذكية للبحث عن مسار لوحة التحكم الصحيح وتجنب أخطاء البناء"""
    possible_endpoints = [
        'admin_dashboard_bp.dashboard',
        'admin_dashboard.dashboard',
        'admin.dashboard',
        'dashboard',
        'admin_dashboard_bp.index',
        'admin.index'
    ]
    for endpoint in possible_endpoints:
        try:
            return url_for(endpoint)
        except BuildError:
            continue
    return '/'

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    """بوابة دخول موحدة للمالك وموظفي الإدارة."""
    
    # 1. التحقق من وجود جلسة فعالة
    if current_user.is_authenticated and session.get('user_type') in ['admin', 'staff']:
        return redirect(get_admin_dashboard_url())

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = None
        user_type = None

        # 2. التحقق من المالك (AdminUser) أولاً
        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            user = admin
            user_type = 'admin'
        else:
            # 3. التحقق من موظف الإدارة (AdminStaff)
            staff = AdminStaff.query.filter_by(username=username).first()
            if staff and staff.check_password(password):
                user = staff
                user_type = 'staff'
        
        # 4. معالجة الدخول
        if user and user.is_active:
            login_user(user, remember=True)
            session['user_type'] = user_type
            
            flash(f'مرحباً بك يا {user.role}.', 'success')
            
            # التوجيه الذكي والآمن للوحة التحكم
            return redirect(get_admin_dashboard_url())
        else:
            flash('بيانات دخول غير صحيحة أو الحساب غير مفعل.', 'danger')
            
    return render_template('auth/login.html')

@auth_portal.route('/logout')
def logout():
    """تسجيل الخروج مع مسح شامل للجلسة."""
    logout_user()
    session.clear() 
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('auth_portal.login'))
