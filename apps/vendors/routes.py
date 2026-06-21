from flask import Blueprint, render_template, request, jsonify
from apps.vendors.vendor_auth_service import VendorAuthService # سنستخدم الخدمة هنا
from apps.models.otp_db import OTPVerification

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    # منطق بدء الدخول
    if VendorAuthService.initiate_login(email, phone):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "فشل الإرسال"}), 400

@vendors_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    if OTPVerification.verify_otp(data.get('email'), data.get('otp')):
        # هنا يتم توجيه المورد إلى لوحة الإعدادات
        return jsonify({"status": "success", "redirect": "/vendors/setup"})
    return jsonify({"status": "error", "message": "رمز التحقق خاطئ"}), 400
