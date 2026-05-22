# coding: utf-8
# ⚙️ محرك تعميد وإدارة الموردين المتكامل - منصة محجوب أونلاين 2026

import os
from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from . import admin_suppliers_bp
from apps.models.supplier_db import Supplier, db
from apps.models.wallet_db import SupplierWallet

# الامتدادات المسموح برفعها للوثائق السيادية
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_suppliers_bp.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    field_type = request.args.get('type')
    value = request.args.get('value')

    if not field_type or not value:
        return jsonify({"exists": False})

    exists = False
    if field_type == 'username':
        exists = Supplier.query.filter_by(username=value).first() is not None
    elif field_type == 'identity_number':
        exists = Supplier.query.filter_by(identity_number=value).first() is not None
    elif field_type == 'owner_phone':
        exists = Supplier.query.filter_by(owner_phone=value).first() is not None
    elif field_type == 'get_next_sequence':
        count = Supplier.query.count()
        next_id = f"SUP-MAH{9631 + count}"
        # توليد كود محفظة متوقع تماشياً مع المعرف المتوقع
        next_wallet = f"WLT-MAH{1120 + count}"
        return jsonify({"next_sequence": next_id, "next_wallet": next_wallet})

    return jsonify({"exists": exists})

@admin_suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_submit():
    if request.method == 'POST':
        try:
            # فصل البيانات النصية القادمة من الـ Form
            data = request.form
            
            # معالجة رفع ملف صورة الوثيقة بأمان إن وجد
            identity_image_filename = None
            if 'identity_image' in request.files:
                file = request.files['identity_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # حفظ الملف في مجلد الرفع المخصص للتطبيق
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'identities')
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, filename))
                    identity_image_filename = filename

            # 1. إنشاء كائن المورد وتعبئة كافة البيانات السيادية والمالية الواردة من الواجهة
            new_supplier = Supplier(
                username=data.get('username'),
                # تأكد من تشفير كلمة المرور في الموديل أو هنا إذا كان الموديل يدعم ذلك
                password_hash=data.get('password'), 
                identity_type=data.get('identity_type'),
                identity_number=data.get('identity_number'),
                identity_image=identity_image_filename,
                owner_name=data.get('owner_name'),
                trade_name=data.get('trade_name'),
                owner_phone=data.get('owner_phone'),
                province=data.get('province'),
                district=data.get('district'),
                address_detail=data.get('address_detail'),
                bank_name=data.get('bank_name'),
                bank_acc=data.get('bank_acc'),
                sovereign_id=data.get('sovereign_id')
            )
            
            db.session.add(new_supplier)
            db.session.flush()  # سحب المعرف التلقائي (id) للمورد دون إغلاق الجلسة

            # 2. إنشاء محفظة المورد المالي وتعميدها
            new_wallet = SupplierWallet(
                supplier_id=new_supplier.id, # الربط العلاقتي الآمن (Foreign Key)
                wallet_code=data.get('wallet_code') if data.get('wallet_code') else f"WLT-MAH{1120 + Supplier.query.count() - 1}"
            )
            
            db.session.add(new_wallet)
            db.session.commit() # تعميد كلي في قاعدة البيانات
            
            return jsonify({"status": "success", "message": "تم تعميد المورد بنجاح وإنشاء المحفظة المالية بنجاح."})

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"خطأ في التعميد السيادي: {str(e)}"}), 500

    return render_template('admin/add_supplier.html')
