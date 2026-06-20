# coding: utf-8
# 📂 apps/vendors/routes.py

from flask import Blueprint, request, jsonify, session
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.vendors.vendor_auth_service import trigger_otp_process, verify_vendor_otp
from werkzeug.security import generate_password_hash

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
    data = request.get_json()
    email = data.get('email')
    # دمج مفتاح الدولة مع الرقم لضمان التنسيق الدولي الكامل
    phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    # البحث عن المورد
    supplier = Supplier.query.filter_by(_owner_email=email).first() 
    
    if supplier:
        trigger_otp_process(email, phone)
        return jsonify({"status": "existing_user", "message": "تم العثور على حسابك، يرجى إدخال الرمز المرسل"})
    else:
        return jsonify({"status": "new_partner", "message": "مرحباً بك كشريك جديد"})

@vendors_bp.route('/register-complete', methods=['POST'])
def register_complete():
    data = request.get_json()
    full_phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    try:
        # 1. إنشاء المورد الأساسي
        new_supplier = Supplier(
            username=data['username'],
            owner_email=data['email'],
            owner_phone=full_phone, # حفظ الرقم المدمج والمشفر
            password_hash=generate_password_hash(data['password']),
            trade_name=data['trade_name']
        )
        new_supplier.generate_codes()
        db.session.add(new_supplier)
        db.session.flush() 
        
        # 2. إنشاء الملف التجاري المتقدم
        new_profile = SupplierProfile(
            user_id=new_supplier.id,
            trade_name=data['trade_name'],
            owner_name=data.get('owner_name'), # الحقل الجديد
            bank_acc=data.get('bank_acc')      # الحقل الجديد
        )
        db.session.add(new_profile)
        db.session.commit()
        
        # 3. تفعيل عملية التحقق
        trigger_otp_process(data['email'], full_phone)
        
        return jsonify({"status": "success", "message": "تم إنشاء حسابك، بانتظار التحقق من واتساب"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@vendors_bp.route('/verify-otp', methods=['POST'])
def verify():
    data = request.get_json()
    if verify_vendor_otp(data.get('email'), data.get('otp')):
        session['vendor_authenticated'] = True
        return jsonify({"status": "success", "redirect": "/vendors/dashboard"})
    
    return jsonify({"status": "error", "message": "الرمز غير صحيح"}), 400
