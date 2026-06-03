# coding: utf-8
# 📂 apps/auth_portal/routes.py - مسارات المصادقة المحصنة بالتخفي والتأمين السيادي

import os
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db

# استيراد البلوبرينت المعرف في __init__.py
from . import auth_blueprint

# 🔑 جلب المسار السري لصفحة الدخول من إعدادات خادم Render
# سيستخدم المسار الافتراضي /gatekeeper_secure_entry_2026 إذا لم يوجد متغير بيئة
SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/gatekeeper_secure_entry_2026')

# -------------------------------------------------------------------------
# 1. 🔥 المسار السري الحقيقي (الدخول المعتمد للمنصة)
# -------------------------------------------------------------------------
@auth_blueprint.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    """المسار الذي يتم فيه التحقق الفعلي من هوية المالك"""
    from apps.models.admin_db import AdminUser
    
    # إذا كان المستخدم مسجلاً دخوله مسبقاً، وجهه للوحة التحكم
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = str(request.form.get('username', '')).strip()
        password = request.form.get('password', '')
        
        # استعلام عن المستخدم
        user = AdminUser.query.filter_by(username=username).first()
        
        # التحقق من البيانات والمطابقة الأمنية
        if user and user.check_password(password):
            if user.role in ['Owner', 'Admin']:
                login_user(user)
                return redirect(url_for('admin_dashboard.dashboard'))
            else:
                flash('ليس لديك صلاحيات الوصول.', 'warning')
        else:
            flash('بيانات الدخول غير صحيحة.', 'danger')
    
    return render_template('auth/login.html')

# -------------------------------------------------------------------------
# 2. 🛡️ مسار الكمين (Decoy Route) لتمويه المخترقين وفحص البوتات
# -------------------------------------------------------------------------
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def decoy_login():
    """طرد برمجيات الفحص الآلي وإيهامهم بأن المسار معطل تماماً"""
    abort(404)

# -------------------------------------------------------------------------
# 3. تسجيل الخروج الآمن
# -------------------------------------------------------------------------
@auth_blueprint.route('/logout')
@login_required
def logout():
    """تسجيل خروج المستخدم وإعادته بأمان للمسار السري"""
    logout_user()
    # استخدام اسم الـ Blueprint المعتمد في التطبيق
    return redirect(url_for('auth_blueprint.login'))
