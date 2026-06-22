# coding: utf-8
# 📂 apps/vendors/routes.py - نظام الدخول السيادي (مؤمن ومحدث للمسارات)

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from apps import db
from apps.vendors.vendor_auth_service import VendorAuthService
from apps.models.otp_db import OTPVerification
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer
import uuid 

# تعريف الـ Blueprint
vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.before_request
def check_login():
    """
    حماية سيادية للمسارات مع ضمان عدم حدوث حلقة إعادة توجيه
    """
    # المسارات المستثناة التي لا تتطلب تسجيل دخول
    # تأكد من أن الـ endpoint يطابق ما يراه Flask
    allowed_endpoints = ['vendors.login', 'static']
    
    if request.endpoint not in allowed_endpoints:
        if not current_user.is_authenticated:
            return redirect(url_for('vendors.login'))

@vendors_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('vendor/login.html')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

        login_type = data.get('type')
        
        # --- أ. دخول المسوقين ---
        if login_type == 'marketer':
            username = data.get('username')
            password = data.get('password')
            user = Marketer.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return jsonify({"status": "success", "redirect": url_for('marketers.dashboard')})
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

        # --- ب. دخول الموردين ---
        raw_phone = data.get('phone', '')
        phone = "".join(filter(str.isdigit, raw_phone))
        otp = data.get('otp')

        if phone and not otp:
            new_otp = OTPVerification.generate_otp(phone)
            if new_otp and VendorAuthService.initiate_login(phone, new_otp):
                return jsonify({"status": "success", "message": "تم إرسال رمز التحقق"})
            return jsonify({"status": "error", "message": "فشل إرسال الرمز"}), 500

        if phone and otp:
            if OTPVerification.verify_otp(phone, otp):
                supplier = Supplier.query.filter_by(owner_phone=phone).first()
                
                # إنشاء مورد جديد إذا كان أول دخول له
                if not supplier:
                    supplier = Supplier(
                        owner_phone=phone,
                        username=f"vendor_{uuid.uuid4().hex[:8]}",
                        password_hash="temp_pass",
                        trade_name="مورد جديد"
                    )
                    db.session.add(supplier)
                    db.session.commit()
                    db.session.refresh(supplier) 
                
                login_user(supplier, remember=True)
                session.permanent = True
                
                # التوجيه الذكي للمورد
                is_ready = getattr(supplier, 'is_setup_complete', False)
                redirect_url = url_for('vendor_dashboard.dashboard') if is_ready else url_for('vendors.setup_profile')
                
                return jsonify({"status": "success", "redirect": redirect_url})
            
            return jsonify({"status": "error", "message": "رمز التحقق خاطئ"}), 400

        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "حدث خطأ في النظام"}), 500

@vendors_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_profile():
    # توجيه المورد إلى قالب الإعداد المخصص
    return render_template('admin/dashboard_content.html', title="إكمال إعدادات المورد")

@vendors_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('vendors.login'))
