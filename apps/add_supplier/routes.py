# coding: utf-8
# ⚙️ محرك تعميد وإدارة الموردين - منصة محجوب أونلاين 2026

from flask import render_template, request, jsonify
from flask_login import login_required
from . import admin_suppliers_bp
from apps.models.supplier_db import Supplier, db
from apps.models.wallet_db import SupplierWallet 

@admin_suppliers_bp.route('/check-duplicate', methods=['GET'])
@login_required
def check_duplicate():
    """
    دالة للتحقق من عدم تكرار البيانات (اسم المستخدم، رقم الهاتف، إلخ)
    """
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
        # منطق جلب المعرف التالي (يمكنك تطويره لاحقاً)
        count = Supplier.query.count()
        next_id = f"SUP-MAH{9631 + count}"
        return jsonify({"next_sequence": next_id})

    return jsonify({"exists": exists})

@admin_suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier_submit():
    """
    مسار تعميد مورد جديد - معالجة نموذج التقديم
    """
    if request.method == 'POST':
        try:
            # استلام البيانات
            data = request.form
            
            # حفظ المورد
            new_supplier = Supplier(
                username=data.get('username'),
                owner_name=data.get('owner_name'),
                trade_name=data.get('trade_name'),
                owner_phone=data.get('owner_phone'),
                identity_number=data.get('identity_number'),
                identity_type=data.get('identity_type'),
                sovereign_id=data.get('sovereign_id') # القيمة القادمة من الحقل المخفي
            )
            db.session.add(new_supplier)
            
            # إنشاء محفظة المورد
            new_wallet = SupplierWallet(
                supplier_id=data.get('sovereign_id'),
                wallet_code=data.get('wallet_code')
            )
            db.session.add(new_wallet)
            
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "تم تعميد المورد بنجاح",
                "data": {
                    "sovereign_id": data.get('sovereign_id'),
                    "wallet_code": data.get('wallet_code')
                }
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    # التعديل هنا: مسار القالب الصحيح بناءً على هيكل مجلداتك
    return render_template('admin/add_supplier.html')

@admin_suppliers_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers_data():
    suppliers = Supplier.query.all()
    return render_template('admin/list.html', suppliers=suppliers)
