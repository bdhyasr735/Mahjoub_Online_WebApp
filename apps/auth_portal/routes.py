# coding: utf-8
# 📂 apps/auth_portal/routes.py - بوابة الدخول السيادية (النسخة النهائية المتوافقة)

import random
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from apps.auth_portal.auth_service import AdminAuthService
from apps.models.admin_db import AdminUser

# تعريف الـ Blueprint مع اسم النطاق الصحيح
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/m7jb_sovereign_hq_v2_99x', methods=['GET', 'POST'])
def login():
    """
    المرحلة 1: التحقق من الهوية وكلمة المرور ثم إرسال الـ OTP.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المسؤول
        admin = AdminUser.query.filter_by(username=username).first()
        
        # التأكد من وجود المستخدم ومطابقة كلمة المرور باستخدام الموديل
        if admin and admin.check_password(password):
            # توليد رمز عشوائي
            otp_code = str(random.randint(100000, 999999))
            
            # محاولة الإرسال
            if AdminAuthService.initiate_login(admin.phone_number, otp_code):
                session['otp_code'] = otp_code
                session['user_id'] = admin.id
                return redirect(url_for('auth_portal.verify_otp_page'))
            else:
                flash("فشل الاتصال بخدمة الإرسال، حاول لاحقاً.")
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة.")
            
    return render_template('auth/login.html')

@auth_portal.route('/verify', methods=['GET', 'POST'])
def verify_otp_page():
    """
    المرحلة 2: التحقق من رمز OTP.
    """
    if 'otp_code' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        user_otp = request.form.get('otp_code')
        
        if user_otp == session.get('otp_code'):
            # إزالة الرمز من الجلسة بعد النجاح
            session.pop('otp_code', None)
            return "✅ تم الدخول بنجاح إلى النظام السيادي."
        else:
            flash("رمز التحقق غير صحيح.")
            
    return render_template('auth/verify_otp.html')

@auth_portal.route('/resend', methods=['POST'])
def resend_otp():
    """إعادة إرسال رمز جديد."""
    user_id = session.get('user_id')
    admin = AdminUser.query.get(user_id) if user_id else None
    
    if admin:
        new_otp = str(random.randint(100000, 999999))
        if AdminAuthService.initiate_login(admin.phone_number, new_otp):
            session['otp_code'] = new_otp
            flash("تمت إعادة إرسال الرمز بنجاح.")
        else:
            flash("فشل إعادة الإرسال.")
            
    return redirect(url_for('auth_portal.verify_otp_page'))
