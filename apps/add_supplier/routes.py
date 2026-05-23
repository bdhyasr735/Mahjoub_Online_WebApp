# coding: utf-8
from flask import render_template, request, jsonify, current_app, url_for, redirect
from flask_login import login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash  # قفل أمني لتشفير كلمات المرور 🔒
import os

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from . import admin_suppliers_bp

# 1. دالة التحقق من التكرار والـ Sequences
@admin_suppliers_bp.route('/check_duplicate', methods=['GET'])
@login_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    
    # جلب التسلسلات التالية المتوقعة بناءً على دالة الموديل المتطورة
    if check_type == 'get_next_sequence':
        next_sovereign = Supplier.generate_next_sovereign_id()
        # توليد كود المحفظة التتابعي بناءً على آخر ID مسجل
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id = (last_supplier.id + 1) if last_supplier else 1
        return jsonify({
            'next_sequence': next_sovereign,
            'next_wallet': f"WLT-MAH{1000 + next_id}"
        })

    # التحقق الحوكمي الصارم من وجود البيانات مسبقاً لمنع التكرار
    exists = False
    if check_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    elif check_type == 'identity_number':
        exists = Supplier.query.filter_by(identity_number=value).first() is not None
        
    return jsonify({'exists': bool(exists)})

# 2. دالة التنفيذ (التعميد المزدوج للمورد ومحفظته)
@admin_suppliers_bp.route('/add_supplier_submit', methods=['POST'])
@login_required
def add_supplier_submit():
    try:
        # البيانات الأساسية من النموذج
        sovereign_id = request.form.get('sovereign_id')
        wallet_code = request.form.get('wallet_code')
        
        # 1. معالجة وحفظ وثيقة الهوية المرفوعة
        file = request.files.get('identity_image')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(f"{sovereign_id}_{file.filename}")
            upload_path = current_app.config.get('UPLOAD_FOLDER', 'apps/static/uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))

        # تشفير كلمة المرور بشكل آمن تماماً قبل كتابتها في داتابيز السيستم
        raw_password = request.form.get('password')
        hashed_password = generate_password_hash(raw_password) if raw_password else ""

        # 2. إنشاء كائن المورد بالمسميات الحقيقية للموديل المستقر ✅
        new_supplier = Supplier(
            sovereign_id=sovereign_id,
            username=request.form.get('username'),
            password_hash=hashed_password,  # الحقل الآمن المعتمد
            identity_type=request.form.get('identity_type'),
            identity_number=request.form.get('identity_number'),
            identity_image=filename,
            owner_name=request.form.get('owner_name'),
            owner_phone=request.form.get('owner_phone'),  # تم التصحيح للهيكل الحقيقي
            trade_name=request.form.get('trade_name'),
            shop_phone=request.form.get('shop_phone') if request.form.get('shop_phone') else request.form.get('owner_phone'),  # field إلزامي
            activity_type=request.form.get('activity_type'),
            province=request.form.get('province'),
            district=request.form.get('district'),
            address_detail=request.form.get('address_detail'),
            bank_name=request.form.get('bank_name'),
            bank_acc=request.form.get('bank_acc'),
            wallet_code=wallet_code
        )
        
        # دمج رقم المحل الافتراضي داخل تفاصيل العنوان تلقائياً إن وجد
        shop_num = request.form.get('shop_number')
        if shop_num:
            new_supplier.shop_number = shop_num

        db.session.add(new_supplier)
        
        # 3. إنشاء المحفظة المالية المرتبطة لشركاء النجاح
        new_wallet = SupplierWallet(
            supplier_id=sovereign_id,
            wallet_code=wallet_code,
            status='نشطة',
            balance=0.0
        )
        db.session.add(new_wallet)
        
        # التزام وحفظ الذرة المترابطة (Atomic Commit)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'تم تعميد شريك النجاح بنجاح - المعرف السيادي: {sovereign_id}'})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تعميد المورد: {str(e)}")
        return jsonify({'status': 'error', 'message': f'حدث خطأ تقني أثناء معالجة الطلب: {str(e)}'})

# 3. عرض صفحة إضافة الموردين
@admin_suppliers_bp.route('/add_supplier', methods=['GET'])
@login_required
def add_supplier_page():
    # عند طلب الصفحة عبر AJAX (من القائمة الجانبية)، نعرض المحتوى الداخلي فقط
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/add_supplier.html')
    
    # تم التصحيح الحاسم هنا واستبدال الاسم القديم بالاسم الجديد تماماً لإزالة الـ BuildError وتأمين الإقلاع السليم 🚀 ✅
    return redirect(url_for('admin_dashboard.dashboard'))
