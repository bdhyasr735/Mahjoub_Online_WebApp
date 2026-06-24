# coding: utf-8
# 📂 apps/auth_portal/routes.py - بوابة الدخول السيادية (النسخة الكاملة)

import random
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from apps.auth_portal.auth_service import AdminAuthService

# تعريف الـ Blueprint
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/m7jb_sovereign_hq_v2_99x', methods=['GET', 'POST'])
def login():
    """المرحلة الأولى: إدخال رقم الهاتف وإرسال الرمز"""
    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            flash("يرجى إدخال رقم الهاتف.")
            return render_template('auth/login.html')
        
        # توليد رمز عشوائي
        otp_code = str(random.randint(100000, 999999))
        
        # إرسال الرمز
        if AdminAuthService.initiate_login(phone, otp_code):
            session['otp_code'] = otp_code
            session['otp_phone'] = phone
            return redirect(url_for('auth_portal.verify_otp_page'))
        else:
            flash("فشل إرسال الرمز، تأكد من الرقم.")
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth_portal.route('/verify', methods=['GET', 'POST'])
def verify_otp_page():
    """المرحلة الثانية: التحقق من الرمز المدخل"""
    if 'otp_code' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        user_otp = request.form.get('otp_code')
        if user_otp == session.get('otp_code'):
            # نجاح التحقق - هنا يمكنك إضافة تسجيل دخول المستخدم فعلياً
            session.pop('otp_code', None)
            return "✅ تم التحقق بنجاح! مرحباً بك في محجوب أونلاين."
        else:
            flash("الرمز غير صحيح، حاول مجدداً.")
    
    return render_template('auth/verify_otp.html')

@auth_portal.route('/resend', methods=['POST'])
def resend_otp():
    """إعادة إرسال الرمز"""
    phone = session.get('otp_phone')
    if phone:
        new_otp = str(random.randint(100000, 999999))
        if AdminAuthService.initiate_login(phone, new_otp):
            session['otp_code'] = new_otp
            flash("تمت إعادة إرسال الرمز.")
    return redirect(url_for('auth_portal.verify_otp_page'))

@auth_portal.route('/status', methods=['GET'])
def status():
    return {"status": "active"}
