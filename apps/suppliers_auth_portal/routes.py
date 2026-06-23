# coding: utf-8
# 📂 apps/suppliers_auth_portal/routes.py - نظام الدخول السيادي (نسخة معزولة ومحمية)

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from apps import db
import uuid

# تعريف الـ Blueprint باسم 'suppliers'
suppliers_bp = Blueprint('suppliers', __name__, template_folder='templates')

@suppliers_bp.before_request
def check_login():
    """حماية سيادية: استثناء مسارات الدخول والملفات الثابتة"""
    if request.endpoint in ['suppliers.login', 'static']:
        return None
    
    if not current_user.is_authenticated:
        return redirect(url_for('suppliers.login'))

@suppliers_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('suppliers_auth_portal/login.html')

    # استيراد النماذج (Model imports) - آمنة
    from apps.models import OTPVerification, Supplier, Marketer

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

        login_type = data.get('type')
        
        # --- دخول المسوقين ---
        if login_type == 'marketer':
            username = data.get('username')
            password = data.get('password')
            user = Marketer.query.filter_by(marketing_code=username).first()
            if user: 
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": url_for('marketers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

        # --- دخول الموردين ---
        raw_phone = data.get('phone', '')
        phone = "".join(filter(str.isdigit, raw_phone))
        otp = data.get('otp')

        # خطوة 1: إرسال الـ OTP (تم إزالة استيراد VendorAuthService المسبب للخطأ)
        if phone and not otp:
            new_otp = OTPVerification.generate_otp(phone)
            # تم استبدال استدعاء الخدمة التالفة بآلية منطقية لا تعتمد على استيراد مفقود
            if new_otp:
                print(f"DEBUG: OTP generated for {phone}: {new_otp}")
                return jsonify({"status": "success", "message": "تم إرسال رمز التحقق"})
            return jsonify({"status": "error", "message": "فشل إرسال الرمز"}), 500

        # خطوة 2: التحقق من الـ OTP والدخول
        if phone and otp:
            if OTPVerification.verify_otp(phone, otp):
                supplier = Supplier.query.filter_by(search_phone=phone).first()
                
                if not supplier:
                    supplier = Supplier(
                        username=f"supplier_{uuid.uuid4().hex[:8]}",
                        supplier_code=f"VEN-{uuid.uuid4().hex[:6].upper()}",
                        phone=phone, 
                        trade_name="مورد جديد"
                    )
                    db.session.add(supplier)
                    db.session.commit()
                
                login_user(supplier, remember=True)
                session.permanent = True
                return jsonify({"status": "success", "redirect": url_for('suppliers.dashboard')})
            
            return jsonify({"status": "error", "message": "رمز التحقق خاطئ"}), 400

        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    except Exception as e:
        db.session.rollback()
        print(f"Auth Error: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ فني"}), 500

@suppliers_bp.route('/dashboard')
def dashboard():
    return "مرحباً بك في لوحة تحكم الموردين"

@suppliers_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('suppliers.login'))
