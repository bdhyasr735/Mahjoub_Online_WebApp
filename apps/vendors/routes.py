# coding: utf-8
# 📂 apps/vendors/routes.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_user, login_required, logout_current_user
from apps.vendors.vendor_auth_service import VendorAuthService
from apps.models.otp_db import OTPVerification
from apps.models.supplier_db import Supplier

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('vendor/login.html')

    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')

    # مرحلة 1: طلب الرمز (Login Request)
    if phone and not otp:
        if VendorAuthService.initiate_login(phone):
            return jsonify({"status": "success", "message": "تم إرسال الرمز إلى واتساب"})
        return jsonify({"status": "error", "message": "فشل في إرسال الرمز"}), 500

    # مرحلة 2: التحقق من الرمز (Verification Request)
    if phone and otp:
        if OTPVerification.verify_otp(phone, otp):
            # التحقق من وجود المورد في قاعدة البيانات
            supplier = Supplier.query.filter_by(_owner_phone=phone).first() # تأكد من آلية البحث هنا
            
            # إذا كان موجوداً نسجل دخوله
            if supplier:
                login_user(supplier)
                return jsonify({"status": "success", "redirect": "/vendors/dashboard"})
            
            # إذا كان مستخدماً جديداً، يمكن توجيهه لصفحة التسجيل أو إكمال البيانات
            return jsonify({"status": "success", "redirect": "/vendors/setup"})
        
        return jsonify({"status": "error", "message": "رمز التحقق غير صحيح أو منتهي"}), 400

@vendors_bp.route('/quick-login', methods=['POST'])
def quick_login():
    """دخول سريع للمطورين أو للعمليات الخاصة"""
    # يفضل تقييد هذا المسار بمستوى صلاحية معين
    return jsonify({"status": "success", "redirect": "/vendors/dashboard"})

@vendors_bp.route('/dashboard')
@login_required
def dashboard():
    return "مرحباً بك في لوحة تحكم المورد"

@vendors_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_profile():
    # هنا سيقوم المورد بتعبئة بياناته في supplier_profile_db.py
    return "صفحة إكمال بيانات المورد"
