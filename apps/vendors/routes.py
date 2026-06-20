# coding: utf-8
# 📂 apps/vendors/routes.py

import os
from flask import Blueprint, request, jsonify, session, render_template
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from werkzeug.security import generate_password_hash
from apps.utils.security import AESCipher
from apps.vendors.vendor_auth_service import trigger_otp_process, verify_vendor_otp, vendor_login_required

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/', methods=['GET'])
def index():
    pending_email = session.get('pending_otp_email')
    return render_template('vendor/login.html', pending_email=pending_email)

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
    print("DEBUG: auth_gateway was reached!") # سطر تشخيصي
    data = request.get_json()
    email = data.get('email')
    
    try:
        encrypted_email = AESCipher.encrypt(email)
        print(f"DEBUG: Searching for: {email} -> Encrypted: {encrypted_email}")
        
        supplier = Supplier.query.filter_by(_owner_email=encrypted_email).first() 
        
        if supplier:
            print(f"DEBUG: Supplier found: {supplier.trade_name}")
            trigger_otp_process(email, supplier.full_phone)
            session['pending_otp_email'] = email 
            return jsonify({"status": "existing_user", "message": "تم إرسال الرمز"})
        else:
            print("DEBUG: Supplier not found in database.")
            return jsonify({"status": "new_partner", "message": "مرحباً بك كشريك جديد"})
            
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي"}), 500

@vendors_bp.route('/register-complete', methods=['POST'])
def register_complete():
    data = request.get_json()
    email = data.get('email')
    full_phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    if Supplier.query.filter_by(_owner_email=AESCipher.encrypt(email)).first():
        return jsonify({"status": "error", "message": "هذا البريد مسجل مسبقاً"}), 400

    try:
        new_supplier = Supplier(
            username=data['username'],
            owner_email=email, # الـ setter سيقوم بالتشفير تلقائياً
            owner_phone=full_phone,
            password_hash=generate_password_hash(data['password']),
            trade_name="جديد" 
        )
        new_supplier.generate_codes()
        db.session.add(new_supplier)
        db.session.flush() 
        
        new_profile = SupplierProfile(user_id=new_supplier.id, trade_name="جديد")
        db.session.add(new_profile)
        db.session.commit()
        
        trigger_otp_process(email, full_phone)
        session['pending_otp_email'] = email
        return jsonify({"status": "success", "message": "تم إنشاء حسابك، يرجى إدخال رمز التحقق"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@vendors_bp.route('/verify-otp', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    if verify_vendor_otp(email, otp):
        session['vendor_authenticated'] = True
        session['vendor_email'] = email
        session.pop('pending_otp_email', None)
        return jsonify({"status": "success", "redirect": "/vendors/dashboard"})
    return jsonify({"status": "error", "message": "الرمز غير صحيح"}), 400

@vendors_bp.route('/dashboard')
def dashboard():
    @vendor_login_required
    def protected_dashboard():
        return "مرحباً بك في لوحة تحكم الموردين"
    return protected_dashboard()
