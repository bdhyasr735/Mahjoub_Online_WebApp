# coding: utf-8
# 📂 apps/vendors/routes.py

import os
from flask import Blueprint, request, jsonify, session, render_template
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from werkzeug.security import generate_password_hash

# إعداد مسار القوالب (يبقى كما هو لأنه لا يسبب حلقة استيراد)
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

vendors_bp = Blueprint('vendors', __name__, template_folder=template_dir)

# --- المسار الجذري ---
@vendors_bp.route('/', methods=['GET'])
def index():
    return render_template('vendor/login.html')

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
    # تحميل المتطلبات هنا فقط (Lazy Import) لكسر حلقة الاستيراد
    from apps.vendors.vendor_auth_service import trigger_otp_process
    
    data = request.get_json()
    email = data.get('email')
    phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    supplier = Supplier.query.filter_by(_owner_email=email).first() 
    
    if supplier:
        trigger_otp_process(email, phone)
        return jsonify({"status": "existing_user", "message": "تم العثور على حسابك، يرجى إدخال الرمز المرسل"})
    else:
        return jsonify({"status": "new_partner", "message": "مرحباً بك كشريك جديد"})

@vendors_bp.route('/register-complete', methods=['POST'])
def register_complete():
    # تحميل المتطلبات هنا فقط
    from apps.vendors.vendor_auth_service import trigger_otp_process
    
    data = request.get_json()
    email = data.get('email')
    full_phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    if Supplier.query.filter_by(_owner_email=email).first():
        return jsonify({"status": "error", "message": "هذا البريد الإلكتروني مسجل مسبقاً"}), 400

    try:
        new_supplier = Supplier(
            username=data['username'],
            owner_email=email,
            owner_phone=full_phone,
            password_hash=generate_password_hash(data['password']),
            trade_name="جديد" 
        )
        new_supplier.generate_codes()
        db.session.add(new_supplier)
        db.session.flush() 
        
        new_profile = SupplierProfile(
            user_id=new_supplier.id,
            trade_name="جديد",
            owner_name="غير محدد",
            bank_acc="غير محدد"
        )
        db.session.add(new_profile)
        db.session.commit()
        
        trigger_otp_process(email, full_phone)
        
        return jsonify({"status": "success", "message": "تم إنشاء حسابك، بانتظار التحقق من واتساب"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "حدث خطأ أثناء التسجيل: " + str(e)}), 500

@vendors_bp.route('/verify-otp', methods=['POST'])
def verify():
    # تحميل المتطلبات هنا فقط
    from apps.vendors.vendor_auth_service import verify_vendor_otp
    
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    if verify_vendor_otp(email, otp):
        session['vendor_authenticated'] = True
        session['vendor_email'] = email
        return jsonify({"status": "success", "redirect": "/vendors/dashboard"})
    
    return jsonify({"status": "error", "message": "الرمز غير صحيح أو انتهت صلاحيته"}), 400

@vendors_bp.route('/dashboard')
def dashboard():
    # تحميل المتطلبات هنا فقط
    from apps.vendors.vendor_auth_service import vendor_login_required
    
    # نقوم بتطبيق الديكوريتور يدوياً هنا لتجنب حلقة الاستيراد في أعلى الملف
    @vendor_login_required
    def protected_dashboard():
        return "مرحباً بك في لوحة تحكم الموردين - محجوب أونلاين"
    
    return protected_dashboard()
