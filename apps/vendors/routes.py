# coding: utf-8
# 📂 apps/vendors/routes.py

from flask import Blueprint, request, jsonify, session, render_template
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from apps.vendors.vendor_auth_service import trigger_otp_process, verify_vendor_otp, vendor_login_required
from werkzeug.security import generate_password_hash

vendors_bp = Blueprint('vendors', __name__)

# --- المسار الجذري لحل مشكلة 404 ---
@vendors_bp.route('/', methods=['GET'])
def index():
    # هذا هو المسار الذي سيعرض صفحة الـ HTML الخاصة بك
    return render_template('vendors/login.html')

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
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
    data = request.get_json()
    email = data.get('email')
    full_phone = f"{data.get('country_code', '')}{data.get('phone', '')}"
    
    # تحقق من عدم وجود البريد مسبقاً
    if Supplier.query.filter_by(_owner_email=email).first():
        return jsonify({"status": "error", "message": "هذا البريد الإلكتروني مسجل مسبقاً"}), 400

    try:
        # 1. إنشاء المورد الأساسي بقيم أولية
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
        
        # 2. إنشاء الملف التجاري المتقدم بقيم افتراضية
        new_profile = SupplierProfile(
            user_id=new_supplier.id,
            trade_name="جديد",
            owner_name="غير محدد",
            bank_acc="غير محدد"
        )
        db.session.add(new_profile)
        db.session.commit()
        
        # 3. إرسال رمز التحقق
        trigger_otp_process(email, full_phone)
        
        return jsonify({"status": "success", "message": "تم إنشاء حسابك، بانتظار التحقق من واتساب"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "حدث خطأ أثناء التسجيل: " + str(e)}), 500

@vendors_bp.route('/verify-otp', methods=['POST'])
def verify():
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

# مسار تجريبي للوحة التحكم
@vendors_bp.route('/dashboard')
@vendor_login_required
def dashboard():
    return "مرحباً بك في لوحة تحكم الموردين - محجوب أونلاين"
