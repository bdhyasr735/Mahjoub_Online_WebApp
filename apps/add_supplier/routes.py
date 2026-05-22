# coding: utf-8
from flask import render_template, request, jsonify, current_app, url_for, redirect
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

# الاستيراد الموحد من ملف extensions لضمان عدم حدوث Circular Import
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp

# 1. دالة التحقق من التكرار (الأمان اللحظي)
@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    if check_type == 'get_next_sequence':
        # جلب أحدث تسلسل وتوليد التالي
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

# 2. دالة التنفيذ (التعميد المزدوج)
@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # معالجة رفع الوثيقة
        file = request.files.get('identity_image')
        filename = None
        if file:
            filename = secure_filename(f"{sovereign_id}_{file.filename}")
            upload_path = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))

        # إنشاء سجل المورد
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
        
        # إنشاء المحفظة المالية المرتبطة
        new_wallet = SupplierWallet(
            supplier_id=sovereign_id,
            wallet_code=wallet_code,
            status='نشطة',
            balance=0.0
        )
        db.session.add(new_wallet)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'تم تعميد المورد بنجاح (معرف: {sovereign_id})'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 3. عرض الصفحة (مع دعم التقديم الديناميكي الاحترافي)
@admin_suppliers_bp.route('/add_supplier', methods=['GET'])
@login_required
def add_supplier_page():
    # هذا الشرط يمنع تكرار الهيكل (Header/Sidebar) عند جلب المحتوى عبر AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/add_supplier.html')
    
    # إذا تم الوصول للرابط مباشرة، يتم توجيه المستخدم للوحة التحكم
    return redirect(url_for('admin_dashboard.dashboard_home'))
