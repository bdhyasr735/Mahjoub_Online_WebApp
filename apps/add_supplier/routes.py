import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from apps.models import db, Supplier, User  # افترضت وجود هذه النماذج في مشروعك
from apps.utils import admin_required  # صالحة للتحقق من صلاحيات المشرف

add_supplier_bp = Blueprint('add_supplier', __name__)

# إعدادات رفع الصور
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@add_supplier_bp.route('/admin/suppliers/add', methods=['GET', 'POST'])
@admin_required
def add_supplier():
    if request.method == 'POST':
        # 1. استلام البيانات الأساسية
        unified_id = request.form.get('unified_id')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 2. معالجة بيانات الهوية (اختيار أو يدوي)
        identity_type = request.form.get('identity_type')
        if identity_type == 'manual':
            identity_type = request.form.get('manual_identity_type')
        identity_number = request.form.get('identity_number')
        
        # 3. بيانات المالك والمنشأة
        owner_name = request.form.get('owner_name')
        trade_name = request.form.get('trade_name')
        shop_phone = request.form.get('shop_phone')
        province = request.form.get('province')
        district = request.form.get('district')
        address = request.form.get('address')
        
        # 4. الربط المالي (اختيار أو يدوي)
        fin_type = request.form.get('fin_type')
        bank_name = request.form.get('bank_name')
        if bank_name == 'manual':
            bank_name = request.form.get('manual_bank_name')
        bank_acc = request.form.get('bank_acc')
        
        # 5. فئة المورد (اختيار أو يدوي)
        category = request.form.get('category')
        if category == 'manual':
            category = request.form.get('manual_category')

        # 6. معالجة رفع صورة الوثيقة
        file = request.files.get('identity_image')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{unified_id}_{file.filename}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'suppliers_ids')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))

        try:
            # إنشاء سجل المورد الجديد
            new_supplier = Supplier(
                unified_id=unified_id,
                username=username,
                identity_type=identity_type,
                identity_number=identity_number,
                identity_image=filename,
                owner_name=owner_name,
                trade_name=trade_name,
                shop_phone=shop_phone,
                province=province,
                district=district,
                address=address,
                fin_type=fin_type,
                bank_name=bank_name,
                bank_acc=bank_acc,
                category=category
            )
            # تعيين كلمة المرور (يفضل استخدام hash)
            new_supplier.set_password(password) 
            
            db.session.add(new_supplier)
            db.session.commit()
            
            flash(f'تم اعتماد المورد {trade_name} بنجاح بالمعرف {unified_id}', 'success')
            return redirect(url_for('add_supplier.list_suppliers')) # أو أي مسار آخر

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء الحفظ: {str(e)}', 'danger')

    # حساب المعرف القادم (Next ID) للعرض في القالب
    last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
    next_id = (last_supplier.id + 1) if last_supplier else 1
    
    return render_template('admin/add_supplier.html', next_id=next_id)

# --- نظام التحقق اللحظي (Ajax Validation) ---

@add_supplier_bp.route('/admin/suppliers/check-duplicate/', methods=['GET'])
@admin_required
def check_duplicate():
    check_type = request.args.get('type')
    value = request.args.get('value')
    bank_name = request.args.get('bank_name')

    exists = False

    if check_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    
    elif check_type == 'trade_name':
        exists = Supplier.query.filter_by(trade_name=value).first() is not None

    elif check_type == 'shop_phone':
        exists = Supplier.query.filter_by(shop_phone=value).first() is not None

    elif check_type == 'bank_acc':
        # التحقق من تكرار رقم الحساب لنفس البنك فقط
        exists = Supplier.query.filter_by(bank_acc=value, bank_name=bank_name).first() is not None

    return jsonify({'exists': exists})
