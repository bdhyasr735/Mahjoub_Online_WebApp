# 📂 apps/vendors/routes.py
import os
from flask import Blueprint, request, jsonify, session, render_template
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_profile_db import SupplierProfile
from werkzeug.security import generate_password_hash
from apps.utils.security import AESCipher # استيراد أداة التشفير
from apps.vendors.vendor_auth_service import trigger_otp_process, verify_vendor_otp, vendor_login_required

vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

@vendors_bp.route('/', methods=['GET'])
def index():
    pending_email = session.get('pending_otp_email')
    return render_template('vendor/login.html', pending_email=pending_email)

@vendors_bp.route('/auth-gateway', methods=['POST'])
def auth_gateway():
    data = request.get_json()
    email = data.get('email')
    # تشفير الإيميل للبحث في القاعدة
    encrypted_email = AESCipher.encrypt(email)
    
    # البحث باستخدام الإيميل المشفر
    supplier = Supplier.query.filter_by(_owner_email=encrypted_email).first() 
    
    if supplier:
        # استخدام full_phone الخاص بالكلاس الذي قمت أنت بتعريفه
        trigger_otp_process(email, supplier.full_phone)
        session['pending_otp_email'] = email 
        return jsonify({"status": "existing_user", "message": "تم إرسال الرمز"})
    else:
        # إذا كان مستخدم جديد، يمكنك هنا حفظ بياناته مؤقتاً أو الرد ليقوم بالتسجيل
        return jsonify({"status": "new_partner", "message": "مرحباً بك كشريك جديد"})

# ... باقي الدوال تبقى كما هي مع التأكد من استخدام AESCipher.encrypt(email) عند البحث عن المورد ...
