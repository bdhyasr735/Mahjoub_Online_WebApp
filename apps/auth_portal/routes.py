# coding: utf-8
# 📂 apps/auth_portal/routes.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from apps.models.admin_db import AdminUser

# [التنظيم السيادي]: ربط المسارات وتحديد المسار الأساسي
auth_portal = Blueprint(
    'auth_portal', 
    __name__, 
    template_folder='templates',
    url_prefix='/auth'
)

# [صمام الخصوصية]: مسار دخول مخفي ومعتمد على متغير بيئة (Environment Variable)
# الرابط سيكون: /auth/m7jb_sovereign_hq_v2_99x
LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

@auth_portal.route(LOGIN_PATH, methods=['GET', 'POST'])
def login():
    # [التحقق من الجلسة]: منع إعادة الدخول للمسؤولين المتصلين بالفعل
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # [البحث السيادي]: جلب بيانات المسؤول من قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        # [التحقق الأمني]: التحقق من وجود المستخدم وكلمة المرور عبر PBKDF2
        if admin and admin.check_password(password):
            # تسجيل الدخول مع تفعيل ميزة التذكر
            login_user(admin, remember=True)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            
            # التوجيه الآمن إلى لوحة التحكم المركزية
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            # رسالة خطأ عامة لزيادة الأمان ومنع كشف أسماء المستخدمين
            flash('بيانات الدخول غير صحيحة.', 'danger')
            
    return render_template('auth/login.html')

@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('auth_portal.login'))
