# coding: utf-8
# 📂 apps/auth_portal/routes.py - المسارات المحدثة لنظام التحقق (نسخة متوافقة)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from apps.auth_portal.auth_service import AdminAuthService
from apps.models.admin_db import AdminUser  # تأكد من استيراد موديل المسؤول الخاص بك
import random

# إنشاء Blueprint للـ Auth Portal
# ملاحظة: إذا كان ملف __init__.py يتوقع استيراد 'auth_portal'، يجب أن يكون الاسم هنا متطابقاً
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. التحقق من المستخدم في قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            # 2. توليد الكود
            otp_code = str(random.randint(100000, 999999))
            session['otp_code'] = otp_code
            session['phone'] = admin.phone_number # سحب الرقم من قاعدة البيانات فعلياً
            
            # 3. استدعاء الخدمة المحدثة التي تعمل مع chatId
            if AdminAuthService.initiate_login(admin.phone_number, otp_code):
                flash('تم إرسال رمز التحقق إلى واتساب الخاص بك.', 'success')
                return redirect(url_for('auth_portal.verify_otp'))
            else:
                flash('حدث خطأ أثناء إرسال الرمز. يرجى المحاولة لاحقاً.', 'danger')
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('auth/login.html')

@auth_portal.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    # منع الدخول لصفحة التحقق بدون وجود جلسة (OTP في السشن)
    if 'otp_code' not in session:
        return redirect(url_for('auth_portal.login'))

    if request.method == 'POST':
        user_otp = request.form.get('otp_code')
        
        # التحقق من الكود
        if user_otp == session.get('otp_code'):
            session.pop('otp_code', None)
            session.pop('phone', None)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('admin.dashboard')) # تأكد من وجود مسار باسم admin.dashboard
        else:
            flash('الرمز غير صحيح، حاول مرة أخرى.', 'danger')
            
    return render_template('auth/verify_otp.html')
