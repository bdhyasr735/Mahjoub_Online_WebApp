# coding: utf-8
import re
import os
import logging
from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet, InvalidToken

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp 

# إعداد الـ Logging لتتبع الأخطاء بدقة في Railway/Production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cipher():
    key = current_app.config.get('ENCRYPTION_KEY')
    if not key:
        logger.error("ENCRYPTION_KEY missing in config!")
        return None
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_data(data):
    """تشفير البيانات مع معالجة الأخطاء"""
    if not data: return None
    cipher = get_cipher()
    if not cipher: return str(data) # احتياط في حال غياب المفتاح
    return cipher.encrypt(str(data).encode()).decode()

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
        try:
            next_sovereign = Supplier.generate_next_sovereign_id()
            # استخراج الأرقام بشكل أكثر أماناً
            clean_num = re.search(r'\d+$', str(next_sovereign))
            clean_num = clean_num.group() if clean_num else "9635"
            return jsonify({
                'next_sequence': next_sovereign,
                'next_wallet': f"WLT-MAH{clean_num}" 
            })
        except Exception as e:
            logger.error(f"Error generating sequence: {e}")
            return jsonify({'error': 'فشل توليد المعرف'}), 500

    exists = False
    if value and value.strip():
        # استخدام getattr مع حماية
        valid_columns = ['username', 'identity_number', 'owner_phone']
        if check_type in valid_columns:
            exists = Supplier.query.filter(getattr(Supplier, check_type) == value.strip()).first() is not None
            
    return jsonify({'available': not bool(exists)})

@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # 1. حفظ الملفات (مع معالجة الأخطاء)
        uploaded_files = request.files.getlist('identity_images')
        saved_filenames = []
        upload_path = current_app.config.get('UPLOAD_FOLDER', 'apps/static/uploads')
        
        if uploaded_files:
            os.makedirs(upload_path, exist_ok=True)
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(f"{sovereign_id}_{file.filename}")
                    file.save(os.path.join(upload_path, filename))
                    saved_filenames.append(filename)
        
        # 2. إنشاء المورد
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            password_hash=generate_password_hash(request.form.get('password')),
            identity_type=request.form.get('identity_type'),
            identity_number=encrypt_data(request.form.get('identity_number')),
            bank_acc=encrypt_data(request.form.get('bank_acc')),
            identity_image=",".join(saved_filenames) if saved_filenames else None,
            owner_name=request.form.get('owner_name'),
            owner_phone=encrypt_data(request.form.get('owner_phone')),
            trade_name=request.form.get('trade_name'),
            shop_number=request.form.get('shop_number'),
            activity_type=request.form.get('activity_type'),
            category=request.form.get('category'),
            province=request.form.get('province'),
            district=request.form.get('district'),
            address_detail=request.form.get('detailed_address'),
            fin_type=request.form.get('fin_type'),
            bank_name=request.form.get('bank_name'),
            wallet_code=wallet_code,
            status='active'
        )
        db.session.add(new_supplier)
        
        # 3. إنشاء المحفظة
        new_wallet = SupplierWallet(supplier_id=sovereign_id, wallet_code=wallet_code, status='نشطة')
        db.session.add(new_wallet)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'تم تعميد شريك النجاح وتشفير بياناته السيادية بنجاح'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Critical error during supplier addition: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': "حدث خطأ داخلي أثناء المعالجة الآمنة"}), 500
