# coding: utf-8
from flask import render_template, request, jsonify, current_app, url_for, redirect
from flask_login import login_required
from werkzeug.utils import secure_filename
import os

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp

# 1. دالة التحقق من التكرار (للتحقق من توافر اسم المستخدم ورقم الهوية)
@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    # جلب التسلسلات التالية المتوقعة (لضمان تدفق البيانات السيادية)
    if check_type == 'get_next_sequence':
        # ملاحظة: في بيئة إنتاج، يفضل استخدام دالة Sequence أو Max ID
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_supplier.id + 1) if last_supplier else 1
        return jsonify({
            'next_sequence': f"SUP-{1000 + next_id}",
            'next_wallet': f"WLT-{1000 + next_id}"
        })

    # التحقق من وجود البيانات مسبقاً
    exists = False
    if check_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    elif check_type == 'identity_number':
        exists = Supplier.query.filter_by(identity_number=value).first() is not None
        
    return jsonify({'exists': bool(exists)})

# 2. دالة التنفيذ (التعميد المزدوج - الذرة المترابطة)
@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        # البيانات الأساسية من النموذج
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # 1. معالجة الوثيقة المرفوعة
        file = request.files.get('identity_image')
        filename = None
        if file and file.filename != '':
            # تأمين الاسم وحفظ الصورة في مجلد الرفع
            filename = secure_filename(f"{sovereign_id}_{file.filename}")
            upload_path = current_app.config.get('UPLOAD_FOLDER', 'apps/static/uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))

        # 2. إنشاء كائن المورد
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            password=request.form.get('password'), # تأكد من تشفيرها في الموديل
            owner_name=request.form.get('owner_name'),
            trade_name=request.form.get('trade_name'),
            identity_type=request.form.get('identity_type'),
            identity_number=request.form.get('identity_number'),
            identity_image=filename, # حفظ المسار في القاعدة
            wallet_code=wallet_code,
            phone=request.form.get('owner_phone'),
            address=request.form.get('address_detail')
        )
        db.session.add(new_supplier)
        
        # 3. إنشاء المحفظة المالية المرتبطة (ربط سيادي)
        new_wallet = SupplierWallet(
            supplier_id=sovereign_id,
            wallet_code=wallet_code,
            status='نشطة',
            balance=0.0
        )
        db.session.add(new_wallet)
        
        # التزام التغييرات (Atomic Commit)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'تم تعميد شريك النجاح بنجاح - المعرف السيادي: {sovereign_id}'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تعميد المورد: {str(e)}")
        return jsonify({'status': 'error', 'message': 'حدث خطأ تقني أثناء معالجة الطلب، يرجى المحاولة لاحقاً.'})

# 3. عرض الصفحة
@admin_suppliers_bp.route('/add_supplier', methods=['GET'])
@login_required
def add_supplier_page():
    # عند طلب الصفحة عبر AJAX (من القائمة الجانبية)، نعرض المحتوى فقط
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/add_supplier.html')
    
    # عند الطلب المباشر، نعيد توجيه المستخدم لهيكل الموقع (Dashboard Shell)
    return redirect(url_for('admin_dashboard.dashboard_home'))
