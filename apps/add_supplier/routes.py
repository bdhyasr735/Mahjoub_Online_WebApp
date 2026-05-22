# coding: utf-8
from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import uuid
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp

# 🛠️ دالة التحقق من التكرار (منع تعميد نفس الهوية أو الاسم مرتين)
@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    if check_type == 'get_next_sequence':
        count = Supplier.query.count() + 1
        return jsonify({
            'next_sequence': f"SUP-{1000 + count}",
            'next_wallet': f"WLT-{1000 + count}"
        })

    exists = False
    if check_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    elif check_type == 'identity_number':
        exists = Supplier.query.filter_by(identity_number=value).first() is not None
        
    return jsonify({'exists': bool(exists)})

# 🚀 دالة تعميد المورد (التعميد المزدوج: مورد + محفظة)
@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        # 1. استلام بيانات المورد
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # 2. معالجة رفع الملف (الوثيقة السيادية)
        file = request.files.get('identity_image')
        filename = None
        if file:
            filename = secure_filename(f"{sovereign_id}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # 3. إنشاء سجل المورد
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            owner_name=request.form.get('owner_name'),
            trade_name=request.form.get('trade_name'),
            identity_type=request.form.get('identity_type'),
            identity_number=request.form.get('identity_number'),
            wallet_code=wallet_code,
            phone=request.form.get('owner_phone'),
            address=request.form.get('address_detail')
        )
        db.session.add(new_supplier)
        
        # 4. إنشاء محفظة المورد المالية (الربط المالي)
        new_wallet = SupplierWallet(
            supplier_id=sovereign_id, # ربط المحفظة بالمورد
            wallet_code=wallet_code,
            status='نشطة'
        )
        db.session.add(new_wallet)
        
        # 5. تثبيت العملية (Atomic Transaction)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'تم تعميد المورد {sovereign_id} بنجاح'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 📋 عرض صفحة تعميد المورد
@admin_suppliers_bp.route('/add_supplier', methods=['GET'])
@login_required
def add_supplier_page():
    return render_template('admin/add_supplier.html')
