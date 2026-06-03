# coding: utf-8
# 📂 apps/auth_portal/routes.py - مسارات الدخول المباشر المحصنة

import os
import time
import random
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from . import auth_portal
from apps.models.admin_db import AdminUser

# مسار الدخول السري (يُجلب من إعدادات البيئة لضمان عدم كشفه في الكود)
SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/gatekeeper_secure_entry_2026')

# -------------------------------------------------------------------------
# 1. المسار السري (الدخول المباشر)
# -------------------------------------------------------------------------
@auth_portal.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    # منع الدخول إذا كان المستخدم مسجلاً بالفعل
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        # استلام آمن للبيانات
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # محرك أمني: تأخير زمني وهمي لمنع هجمات التخمين (Brute Force)
        time.sleep(random.uniform(0.8, 1.5))
        
        # التحقق من وجود المستخدم
        user = AdminUser.query.filter_by(username=username).first()
        error_msg = 'بيانات الدخول غير صحيحة.'

        if user:
            # التحقق من حالة القفل
            if hasattr(user, 'is_locked') and user.is_locked():
                flash('الحساب مقفل مؤقتاً. يرجى الانتظار.', 'danger')
            # التحقق من كلمة المرور (تأكد أن دالة check_password موجودة في الموديل)
            elif user.check_password(password):
                if user.role in ['Owner', 'Admin']:
                    login_user(user)
                    # إعادة تعيين محاولات الفشل
                    if hasattr(user, 'reset_failed_attempts'):
                        user.reset_failed_attempts()
                        db.session.commit()
                    return redirect(url_for('admin_dashboard.dashboard'))
                else:
                    flash(error_msg, 'danger')
            else:
                # تسجيل محاولة فاشلة
                if hasattr(user, 'increment_failed_attempts'):
                    user.increment_failed_attempts()
                    db.session.commit()
                flash(error_msg, 'danger')
        else:
            flash(error_msg, 'danger')
    
    return render_template('auth/login.html')

# -------------------------------------------------------------------------
# 2. مسار الكمين (Decoy) - لخداع البوتات
# -------------------------------------------------------------------------
@auth_portal.route('/login', methods=['GET', 'POST'])
def decoy_login():
    # أي بوت يحاول الوصول لـ /login سيتم طرده فوراً لمنع التجسس
    abort(403)

# -------------------------------------------------------------------------
# 3. تسجيل الخروج
# -------------------------------------------------------------------------
@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_portal.login'))

# -------------------------------------------------------------------------
# 4. مسار الهوية (اختياري - يمكنك حذفه إذا لم تستخدمه)
# -------------------------------------------------------------------------
@auth_portal.route('/upload-identity', methods=['GET', 'POST'])
@login_required
def upload_identity():
    return render_template('auth/upload_id.html')
