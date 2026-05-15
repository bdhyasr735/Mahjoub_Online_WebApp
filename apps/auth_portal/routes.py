# coding: utf-8
# 🔑 بوابة النفاذ - منصة محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from apps import db 
from apps.models.admin_db import AdminUser 
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المدير في قاعدة البيانات المركزية
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # التوجه للوحة التحكم بعد النجاح
            return redirect(url_for('admin_dashboard.index'))
        
        flash('بيانات الدخول غير صحيحة، يرجى التحقق من الصلاحيات.', 'danger')
    
    # 🎯 هنا الربط الصحيح مع مسار القالب الخاص بك
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))
