# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول السيادي (مُحدث بالكامل)

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from apps import db

# الاستيرادات من المجلدات المحدثة
from apps.suppliers_auth_portal.auth_service import VendorAuthService 
from apps.models.otp_db import OTPVerification
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer 
import uuid 

# تعريف الـ Blueprint باسم 'suppliers_portal'
suppliers_bp = Blueprint('suppliers_portal', __name__, template_folder='templates')

@suppliers_bp.before_request
def check_login():
    """حماية سيادية: استثناء مسارات الدخول والملفات الثابتة"""
    if request.endpoint in ['suppliers_portal.login', 'static']:
        return None
    
    if not current_user.is_authenticated:
        return redirect(url_for('suppliers_portal.login'))

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # مسار القالب الصحيح داخل المجلد الجديد
        return render_template('suppliers_auth_portal/login.html')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

        login_type = data.get('type')
        
        # --- دخول المسوقين ---
        if login_type == 'marketer':
            username = data.get('username')
            password = data.get('password')
            user = Marketer.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": url_for('marketers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

        # --- دخول الموردين ---
        raw_phone = data.get('phone', '')
        phone = "".join(filter(str.isdigit, raw_phone))
        otp = data.get('otp')

        # خطوة 1: إرسال الـ OTP
        if phone and not otp:
            new_otp = OTPVerification.generate_otp(phone)
            if new_otp and VendorAuthService.initiate_login(phone, new_otp):
                return jsonify({"status": "success", "message": "تم إرسال رمز التحقق"})
            return jsonify({"status": "error", "message": "فشل إرسال الرمز"}), 500

        # خطوة 2: التحقق من الـ OTP والدخول
        if phone and otp:
            if OTPVerification.verify_otp(phone, otp):
                supplier = Supplier.query.filter_by(owner_phone=phone).first()
                
                if not supplier:
                    supplier = Supplier(
                        owner_phone=phone,
                        username=f"vendor_{uuid.uuid4().hex[:8]}",
                        password_hash="temp_pass",
                        trade_name="مورد جديد"
                    )
                    db.session.add(supplier)
                    db.session.commit()
                
                login_user(supplier, remember=True)
                session.permanent = True
                return jsonify({"status": "success", "redirect": url_for('vendor_dashboard.dashboard')})
            
            return jsonify({"status": "error", "message": "رمز التحقق خاطئ"}), 400

        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    except Exception as e:
        db.session.rollback()
        # طباعة الخطأ في الـ Console للمساعدة في التشخيص
        print(f"Auth Error: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ فني"}), 500

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers_portal.login'))
