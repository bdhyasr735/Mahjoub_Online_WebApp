# coding: utf-8
import re
import os
import base64
from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet # المكتبة المطلوبة للتشفير

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp 

# إعداد مفتاح التشفير (يجب وضعه في ملف الإعدادات .env)
# قم بتوليد مفتاح باستخدام Fernet.generate_key() وحفظه في الإعدادات
ENCRYPTION_KEY = current_app.config.get('ENCRYPTION_KEY', b'your-32-byte-secret-key-here==')
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """تشفير البيانات بنظام AES-256"""
    if not data: return None
    return cipher_suite.encrypt(str(data).encode()).decode()

@admin_suppliers_bp.route('/add_supplier_page', methods=['GET'])
@login_required
def add_supplier_page():
    return render_template('admin/add_supplier.html')

@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    if check_type == 'get_next_sequence':
        next_sovereign = Supplier.generate_next_sovereign_id()
        supplier_digits = re.findall(r'\d+', str(next_sovereign))
        clean_num = supplier_digits[0] if supplier_digits else "9635"
        return jsonify({
            'next_sequence': next_sovereign,
            'next_wallet': f"WLT-MAH{clean_num}" 
        })

    exists = False
    if value and value.strip() != '':
        val = value.strip()
        # إضافة التحقق من فئة النشاط إذا لزم الأمر
        exists = Supplier.query.filter(getattr(Supplier, check_type, None) == val).first() is not None
            
    return jsonify({'available': not bool(exists)})

@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        # البيانات الأساسية
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # حفظ الملفات
        uploaded_files = request.files.getlist('identity_images')
        saved_filenames = []
        upload_path = current_app.config.get('UPLOAD_FOLDER', 'apps/static/uploads')
        if not os.path.exists(upload_path): os.makedirs(upload_path)
            
        for file in uploaded_files:
            if file and file.filename != '':
                filename = secure_filename(f"{sovereign_id}_{file.filename}")
                file.save(os.path.join(upload_path, filename))
                saved_filenames.append(filename)
        
        # إنشاء المورد مع تشفير البيانات الحساسة (AES-256)
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            password_hash=generate_password_hash(request.form.get('password')),
            identity_type=request.form.get('identity_type'),
            # تشفير الحقول الحساسة
            identity_number=encrypt_data(request.form.get('identity_number')),
            bank_acc=encrypt_data(request.form.get('bank_acc')),
            
            identity_image=",".join(saved_filenames) if saved_filenames else None,
            owner_name=request.form.get('owner_name'),
            owner_phone=encrypt_data(request.form.get('owner_phone')),
            trade_name=request.form.get('trade_name'),
            shop_number=request.form.get('shop_number'),
            activity_type=request.form.get('activity_type'), # استلام الفئة من النموذج
            category=request.form.get('category'),           # حقل الفئة الجديد
            province=request.form.get('province'),
            district=request.form.get('district'),
            address_detail=request.form.get('detailed_address'),
            fin_type=request.form.get('fin_type'),
            bank_name=request.form.get('bank_name'),
            wallet_code=wallet_code,
            status='active'
        )
        db.session.add(new_supplier)
        
        # إنشاء المحفظة
        new_wallet = SupplierWallet(supplier_id=sovereign_id, wallet_code=wallet_code, status='نشطة')
        db.session.add(new_wallet)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'تم تعميد شريك النجاح وتشفير بياناته السيادية بنجاح',
            'next_sequence': Supplier.generate_next_sovereign_id(),
            'next_wallet': wallet_code.replace(sovereign_id, str(int(sovereign_id)+1)) # تحديث تلقائي للعداد
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"خطأ في المعالجة الآمنة: {str(e)}"})
