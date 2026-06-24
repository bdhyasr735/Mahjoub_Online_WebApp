# coding: utf-8
# 📂 apps/auth_portal/routes.py - بوابة الدخول السيادية

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from apps.auth_portal.auth_service import AdminAuthService

# تعريف الـ Blueprint - لاحظ أن __name__ ضروري ليتمكن Flask من تحديد المسار
auth_portal = Blueprint('auth_portal', __name__, template_folder='templates')

@auth_portal.route('/m7jb_sovereign_hq_v2_99x', methods=['GET', 'POST'])
def login():
    """
    بوابة تسجيل الدخول الخاصة بالإدارة.
    الرابط الكامل: /auth/m7jb_sovereign_hq_v2_99x
    """
    if request.method == 'POST':
        phone = request.form.get('phone')
        # هنا يتم استدعاء محرك الإرسال (تأكد من وجود منطق توليد OTP)
        # otp_code = "1234" 
        # success = AdminAuthService.initiate_login(phone, otp_code)
        
        return "تم استلام طلب تسجيل الدخول بنجاح."

    return render_template('auth/login.html')

@auth_portal.route('/status', methods=['GET'])
def status():
    """مسار اختبار للتحقق من أن الموديول يعمل"""
    return jsonify({"status": "auth_portal is active", "path": "/auth/m7jb_sovereign_hq_v2_99x"})

# ⚠️ هام جداً: عند حدوث أي خطأ في هذا الموديول، سيظهر في الـ Logs
@auth_portal.errorhandler(404)
def handle_404(e):
    return "خطأ 404: المسار غير موجود داخل auth_portal", 404
