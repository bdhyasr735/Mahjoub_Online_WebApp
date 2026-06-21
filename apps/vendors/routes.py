# coding: utf-8
# 📂 apps/vendors/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_user, login_required
from apps.vendors.vendor_auth_service import VendorAuthService
from apps.models.otp_db import OTPVerification
from apps.models.supplier_db import Supplier

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('vendor/login.html')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "لم يتم استلام بيانات"}), 400

        phone = data.get('phone')
        otp = data.get('otp')

        # مرحلة 1: طلب الرمز
        if phone and not otp:
            # توليد رمز جديد
            new_otp = OTPVerification.generate_otp(phone)
            
            # التأكد من نجاح التوليد قبل محاولة الإرسال
            if new_otp:
                if VendorAuthService.initiate_login(phone, new_otp):
                    return jsonify({"status": "success", "message": "تم إرسال الرمز إلى واتساب"})
                else:
                    return jsonify({"status": "warning", "message": "فشل الاتصال بخدمة واتساب، يرجى المحاولة لاحقاً"}), 200
            else:
                return jsonify({"status": "error", "message": "فشل إنشاء رمز التحقق"}), 500

        # مرحلة 2: التحقق من الرمز
        if phone and otp:
            if OTPVerification.verify_otp(phone, otp):
                supplier = Supplier.query.filter_by(_owner_phone=phone).first()
                if supplier:
                    login_user(supplier)
                    return jsonify({"status": "success", "redirect": "/vendors/dashboard"})
                return jsonify({"status": "success", "redirect": "/vendors/setup"})
            
            return jsonify({"status": "error", "message": "رمز التحقق غير صحيح أو منتهي الصلاحية"}), 400
            
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR in /login: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع في النظام"}), 500

@vendors_bp.route('/dashboard')
@login_required
def dashboard():
    return "مرحباً بك في لوحة تحكم المورد"

@vendors_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_profile():
    return "صفحة إكمال بيانات المورد"
