# coding: utf-8
# 📂 apps/auth_portal/routes.py - البوابة السيادية للإدارة العليا (إصدار نظام HyperSender المحصن V2)

import os
import time
import random
import re
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from apps.extensions import db
from . import auth_portal
from apps.models.admin_db import AdminUser
from apps.models.otp_db import OTPVerification
from apps.auth_portal.auth_service import AdminAuthService 

SECRET_LOGIN_PATH = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')

# جسر إرسال الإدارة (تم التحديث ليتوافق مع V2)
class AdminDispatcher:
    @staticmethod
    def send(phone, code):
        # في نظام V2، الـ API يولد الكود، لذا نرسل الـ phone فقط للخدمة
        return AdminAuthService.initiate_login(phone, code)

def format_phone_number(phone):
    """تصحيح الرقم إلى الصيغة الدولية 967"""
    clean = re.sub(r'[^\d]', '', str(phone))
    if len(clean) == 9 and clean.startswith('7'):
        return '967' + clean
    elif len(clean) == 10 and clean.startswith('07'):
        return '967' + clean[1:]
    return clean

# 1. مسار الدخول الأساسي
@auth_portal.route(SECRET_LOGIN_PATH, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        time.sleep(random.uniform(1.0, 2.0)) # حماية ضد هجمات التوقيت
        
        try:
            user = AdminUser.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('بيانات الدخول غير صحيحة.', 'danger')
                return render_template('auth/login.html')

            raw_phone = getattr(user, 'phone_number', None)
            phone_to_use = format_phone_number(raw_phone)
            
            if not phone_to_use or len(phone_to_use) < 12:
                flash('رقم الهاتف المسجل غير صالح.', 'danger')
                return render_template('auth/login.html')

            session['temp_user_id'] = user.id
            session.pop('_flashes', None)
            
            # إرسال طلب التوثيق عبر الـ Dispatcher
            if OTPVerification.generate_otp(phone_to_use, AdminDispatcher):
                session['last_otp_sent'] = time.time()
                flash('تم إرسال رمز التحقق إلى واتساب الإدارة.', 'info')
                return redirect(url_for('auth_portal.verify_otp_page'))
            else:
                flash('فشل في إرسال الرمز، يرجى المحاولة بعد قليل.', 'danger')
                return render_template('auth/login.html')
                    
        except Exception as e:
            print(f"🚨 خطأ فني في البوابة السيادية: {e}")
            flash('حدث خطأ فني.', 'warning')
    
    return render_template('auth/login.html')

# 2. مسارات التحقق
@auth_portal.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    if 'temp_user_id' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        otp_code = request.form.get('otp_code', '').strip()
        user = AdminUser.query.get(session['temp_user_id'])
        phone_to_use = format_phone_number(user.phone_number)

        # التحقق من الكود (معتمد على منطق OTPVerification المحلي)
        if user and OTPVerification.verify_otp(phone_to_use, otp_code):
            login_user(user)
            session.pop('temp_user_id', None)
            session.pop('last_otp_sent', None)
            if hasattr(user, 'reset_failed_attempts'):
                user.reset_failed_attempts()
                db.session.commit()
            return redirect(url_for('admin_dashboard.dashboard'))
        else:
            session.pop('_flashes', None)
            flash('رمز التحقق غير صحيح أو منتهي.', 'danger')
            
    return render_template('auth/verify_otp.html')

@auth_portal.route('/resend-otp', methods=['POST'])
def resend_otp():
    if 'temp_user_id' in session:
        # حماية ضد إعادة الإرسال المفرط (Cooldown 60s)
        last_sent = session.get('last_otp_sent', 0)
        if time.time() - last_sent < 60:
            flash('يرجى الانتظار دقيقة قبل إعادة طلب الرمز.', 'warning')
            return redirect(url_for('auth_portal.verify_otp_page'))
        
        user = AdminUser.query.get(session['temp_user_id'])
        phone_to_use = format_phone_number(user.phone_number)
        
        if phone_to_use and OTPVerification.generate_otp(phone_to_use, AdminDispatcher):
            session['last_otp_sent'] = time.time()
            flash('تم إرسال رمز جديد بنجاح.', 'info')
        else:
            flash('فشل إعادة الإرسال.', 'danger')
            
    return redirect(url_for('auth_portal.verify_otp_page'))

@auth_portal.route('/login', methods=['GET', 'POST'])
def decoy_login():
    abort(403) 

@auth_portal.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_portal.login'))
