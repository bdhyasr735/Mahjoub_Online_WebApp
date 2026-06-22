# coding: utf-8
# 📂 apps/auth_portal/routes.py - البوابة السيادية (مُحدثة: تم استبدال البريد بـ اسم المستخدم)

import os
import time
import random
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from . import auth_portal
from apps.models.admin_db import AdminUser
from apps.models.otp_db import OTPVerification

# مسار الدخول السري
SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

# -------------------------------------------------------------------------
# 1. مسار الدخول الأساسي
# -------------------------------------------------------------------------
@auth_portal.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        time.sleep(random.uniform(1.0, 2.0))
        
        try:
            user = AdminUser.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                flash('بيانات الدخول غير صحيحة.', 'danger')
                return render_template('auth/login.html')

            if hasattr(user, 'is_locked') and user.is_locked():
                flash('الحساب مقفل مؤقتاً.', 'danger')
                return render_template('auth/login.html')

            if user.role not in ['Owner', 'Admin']:
                flash('ليس لديك صلاحية الدخول.', 'danger')
                return render_template('auth/login.html')

            # استخدام 'username' كمعرف للـ OTP بدلاً من 'email'
            session['temp_user_id'] = user.id
            OTPVerification.generate_otp(user.username) 
            
            flash('تم التحقق، يرجى إدخال رمز التحقق (OTP) المرسل لهاتفك/اسمك.', 'info')
            return redirect(url_for('auth_portal.verify_otp_page'))
                    
        except Exception as e:
            print(f"🚨 خطأ فني: {e}")
            flash('حدث خطأ فني.', 'warning')
    
    return render_template('auth/login.html')

# -------------------------------------------------------------------------
# 2. مسارات التحقق من الـ OTP
# -------------------------------------------------------------------------
@auth_portal.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    if 'temp_user_id' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        user = AdminUser.query.get(session['temp_user_id'])

        # التحقق باستخدام username
        if user and OTPVerification.verify_otp(user.username, otp_code):
            login_user(user)
            session.pop('temp_user_id', None)
            
            if hasattr(user, 'reset_failed_attempts'):
                user.reset_failed_attempts()
                db.session.commit()
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            flash('رمز التحقق غير صحيح.', 'danger')
            
    return render_template('auth/verify_otp.html')

@auth_portal.route('/resend-otp', methods=['POST'])
def resend_otp():
    if 'temp_user_id' in session:
        user = AdminUser.query.get(session['temp_user_id'])
        if user:
            OTPVerification.generate_otp(user.username)
            flash('تم إرسال رمز تحقق جديد.', 'info')
    return redirect(url_for('auth_portal.verify_otp_page'))

# -------------------------------------------------------------------------
# 3. المسارات المساعدة
# -------------------------------------------------------------------------
@auth_portal.route('/login', methods=['GET', 'POST'])
def decoy_login():
    abort(403) 

@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_portal.login'))
