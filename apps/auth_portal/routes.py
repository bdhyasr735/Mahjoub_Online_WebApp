# coding: utf-8
# 📂 apps/auth_portal/routes.py - بوابة الدخول السيادية (نسخة كاملة مع منطق الـ OTP)

import random
from flask import Blueprint, render_template, request, session, jsonify
from apps.auth_portal.auth_service import AdminAuthService

# تعريف الـ Blueprint
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/m7jb_sovereign_hq_v2_99x', methods=['GET', 'POST'])
def login():
    """
    بوابة تسجيل الدخول: إرسال الرمز وتخزينه في الجلسة.
    """
    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            return "يرجى إدخال رقم الهاتف.", 400
        
        # 1. توليد رمز عشوائي مكون من 6 أرقام
        otp_code = str(random.randint(100000, 999999))
        
        # 2. إرسال الرمز عبر خدمة HyperSender
        success = AdminAuthService.initiate_login(phone, otp_code)
        
        if success:
            # 3. تخزين الرمز في الجلسة (Session) للتحقق منه لاحقاً
            session['otp_code'] = otp_code
            session['otp_phone'] = phone
            return "تم إرسال رمز التحقق بنجاح إلى رقمك."
        else:
            return "فشل إرسال الرمز. تأكد من صحة الرقم أو اتصل بالدعم.", 500

    return render_template('auth/login.html')

@auth_portal.route('/verify', methods=['POST'])
def verify():
    """
    مسار التحقق من الرمز المدخل من المستخدم.
    """
    user_otp = request.form.get('otp')
    stored_otp = session.get('otp_code')
    
    if user_otp and user_otp == stored_otp:
        # هنا يتم تسجيل دخول المستخدم فعلياً (Login logic)
        session.pop('otp_code', None) # مسح الرمز بعد استخدامه
        return "تم التحقق بنجاح! مرحبًا بك في محجوب أونلاين."
    
    return "الرمز غير صحيح أو منتهي الصلاحية.", 401

@auth_portal.route('/status', methods=['GET'])
def status():
    """مسار اختبار الحالة"""
    return jsonify({"status": "auth_portal is active", "path": "/auth/m7jb_sovereign_hq_v2_99x"})

@auth_portal.errorhandler(404)
def handle_404(e):
    return "خطأ 404: المسار غير موجود داخل auth_portal", 404
