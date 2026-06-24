# coding: utf-8
# 📂 apps/auth_portal/routes.py - المسارات المحدثة لنظام التحقق

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from apps.auth_portal.auth_service import AdminAuthService
import random

# إنشاء Blueprint للـ Auth Portal
auth_blueprint = Blueprint('auth', __name__, template_folder='templates')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # هنا يجب إضافة منطق التحقق من المستخدم في قاعدة البيانات
        # كمثال: user = User.query.filter_by(username=username).first()
        # إذا نجح التحقق، نولد الكود ونرسله:
        
        otp_code = str(random.randint(100000, 999999))
        session['otp_code'] = otp_code
        session['phone'] = "77xxxxxxxx" # هذا الرقم يجب أن يأتي من قاعدة البيانات
        
        # استدعاء الخدمة المحدثة
        if AdminAuthService.initiate_login(session['phone'], otp_code):
            flash('تم إرسال رمز التحقق إلى واتساب الخاص بك.', 'success')
            return redirect(url_for('auth.verify_otp'))
        else:
            flash('حدث خطأ أثناء إرسال الرمز. يرجى المحاولة لاحقاً.', 'danger')
            
    return render_template('auth/login.html')

@auth_blueprint.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp_code')
        
        # التحقق من الكود
        if user_otp == session.get('otp_code'):
            session.pop('otp_code', None)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('admin.dashboard')) # مسار الداشبورد الخاص بك
        else:
            flash('الرمز غير صحيح، حاول مرة أخرى.', 'danger')
            
    return render_template('auth/verify_otp.html')
