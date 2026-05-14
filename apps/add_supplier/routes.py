import os
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime

admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder='../../templates'
)

@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    # استيراد محلي لتفادي الـ Circular Import تماماً وضمان إقلاع السيرفر
    from models.supplier_db import Supplier
    from apps import db 

    if request.method == 'POST':
        try:
            unified_id = request.form.get('unified_id')
            username = request.form.get('username')
            password = request.form.get('password')
            
            category = request.form.get('category')
            if category == 'manual':
                category = request.form.get('manual_category')

            owner_name = request.form.get('owner_name')
            trade_name = request.form.get('trade_name')
            shop_phone = request.form.get('shop_phone')
            
            province = request.form.get('province')
            district = request.form.get('district')
            address_detail = request.form.get('address') 

            fin_type = request.form.get('fin_type')
            bank_name = request.form.get('bank_name')
            if bank_name == 'manual':
                bank_name = request.form.get('manual_bank_name')
            bank_acc = request.form.get('bank_acc')

            # فحص تكرار البيانات قبل الحفظ
            if Supplier.query.filter_by(username=username).first():
                return jsonify({'status': 'error', 'message': 'اسم المستخدم مسجل مسبقاً!'}), 400
            if Supplier.query.filter_by(trade_name=trade_name).first():
                return jsonify({'status': 'error', 'message': 'الاسم التجاري مسجل مسبقاً!'}), 400

            new_supplier = Supplier(
                sovereign_id=unified_id,
                username=username,
                password=password, 
                category=category,
                owner_name=owner_name,
                trade_name=trade_name,
                shop_phone=shop_phone,
                province=province,
                district=district,
                address_detail=address_detail,
                finance_type=fin_type,
                bank_name=bank_name,
                bank_account=bank_acc,
                created_at=datetime.utcnow()
            )

            db.session.add(new_supplier)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'data': {
                    'sovereign_id': unified_id,
                    'username': username,
                    'password': password
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'حدث خطأ في الخادم: {str(e)}'}), 500

    # معالجة طلب الـ GET وعرض الصفحة
    next_id_num = 1
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier:
            next_id_num = last_supplier.id + 1
    except Exception as e:
        print(f"Warning: Database context fallback: {e}")
        next_id_num = 1
        
    return render_template('admin/add_supplier.html', next_id=next_id_num, next_id_num=next_id_num)


@admin_suppliers.route('/admin/suppliers/check-duplicate', methods=['GET'])
def check_duplicate():
    from models.supplier_db import Supplier 

    check_type = request.args.get('type')
    value = request.args.get('value', '').strip()
    bank_name = request.args.get('bank_name', '').strip()

    if not check_type or not value:
        return jsonify({'exists': False})

    exists = False
    try:
        if check_type == 'username':
            exists = Supplier.query.filter_by(username=value).first() is not None
        elif check_type == 'trade_name':
            exists = Supplier.query.filter_by(trade_name=value).first() is not None
        elif check_type == 'shop_phone':
            exists = Supplier.query.filter_by(shop_phone=value).first() is not None
        elif check_type == 'bank_acc':
            exists = Supplier.query.filter_by(bank_account=value, bank_name=bank_name).first() is not None
    except Exception:
        exists = False

    return jsonify({'exists': exists})
