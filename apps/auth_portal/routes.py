# coding: utf-8
# 📂 apps/auth_portal/routes.py - البوابة السيادية (دخول محصن + مصادقة مزدوجة)

import os
import time
import random
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from . import auth_portal
from apps.models.admin_db import AdminUser
from apps.models.otp_db import OTPVerification

# مسار الدخول السري (يُجلب من إعدادات البيئة)
SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

# -------------------------------------------------------------------------
# 1. مسار الدخول الأساسي (كلمة المرور)
# -------------------------------------------------------------------------
@auth_portal.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # 🛡️ تأخير زمني عشوائي لإحباط هجمات القوة الغاشمة (Brute Force)
        time.sleep(random.uniform(1.0, 2.0))
        
        try:
            user = AdminUser.query.filter_by(username=username).first()
            
            # التحقق من وجود المستخدم وكلمة المرور
            if not user or not user.check_password(password):
                flash('بيانات الدخول غير صحيحة.', 'danger')
                return render_template('auth/login.html')

            # التحقق من حالة القفل
            if hasattr(user, 'is_locked') and user.is_locked():
                flash('الحساب مقفل مؤقتاً بسبب كثرة المحاولات.', 'danger')
                return render_template('auth/login.html')

            # التحقق من الصلاحيات
            if user.role not in ['Owner', 'Admin']:
                flash('ليس لديك صلاحية الدخول لهذه البوابة.', 'danger')
                return render_template('auth/login.html')

            # 🛡️ النجاح في كلمة المرور -> الانتقال لمرحلة الـ OTP
            session['temp_user_id'] = user.id
            OTPVerification.generate_otp(user.email) # توليد وإرسال الرمز
            
            flash('تم التحقق من الهوية، يرجى إدخال رمز التحقق (OTP) المرسل لبريدك.', 'info')
            return redirect(url_for('auth_portal.verify_otp_page'))
                    
        except Exception as e:
            print(f"🚨 خطأ فني في بوابة الدخول: {e}")
            flash('حدث خطأ فني، يرجى المحاولة لاحقاً.', 'warning')
    
    return render_template('auth/login.html')

# -------------------------------------------------------------------------
# 2. مسار التحقق من الـ OTP (المصادقة المزدوجة)
# -------------------------------------------------------------------------
@auth_portal.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    # التأكد من وجود جلسة مؤقتة (لا يمكن الدخول هنا بدون كلمة مرور صحيحة)
    if 'temp_user_id' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        user = AdminUser.query.get(session['temp_user_id'])

        if user and OTPVerification.verify_otp(user.email, otp_code):
            login_user(user)
            session.pop('temp_user_id', None) # تنظيف الجلسة المؤقتة
            
            # إعادة ضبط محاولات الفشل عند الدخول الناجح
            if hasattr(user, 'reset_failed_attempts'):
                user.reset_failed_attempts()
                db.session.commit()
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            flash('رمز التحقق غير صحيح أو منتهي الصلاحية.', 'danger')
            
    return render_template('auth/verify_otp.html')

# -------------------------------------------------------------------------
# 3. المسارات المساعدة (الكمين والخروج)
# -------------------------------------------------------------------------
@auth_portal.route('/login', methods=['GET', 'POST'])
def decoy_login():
    # ⚠️ مسار كمين للمتطفلين (Bot Trapping)
    abort(403) 

@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_portal.login'))
