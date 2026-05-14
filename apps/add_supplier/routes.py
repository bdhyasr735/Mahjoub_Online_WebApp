import os
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime

# حساب مسار القوالب برمجياً لمنع خطأ TemplateNotFound على سيرفر Railway
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', '..', 'templates')

admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder=template_dir
)

# دالة ذكية مستقلة تفحص وتضيف الأعمدة الناقصة لجدول الموردين تلقائياً دون المساس بالبيانات القديمة
def auto_upgrade_supplier_table():
    from apps import db
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('suppliers')]
        
        expected_columns = {
            'category': 'VARCHAR(50)',
            'finance_type': 'VARCHAR(50)',
            'bank_name': 'VARCHAR(100)',
            'bank_account': 'VARCHAR(100)'
        }
        
        for col_name, col_type in expected_columns.items():
            if col_name not in columns:
                db.session.execute(text(f"ALTER TABLE suppliers ADD COLUMN {col_name} {col_type};"))
                db.session.commit()
                print(f"🔧 [Independent Upgrade] Added column: {col_name}")
    except Exception as e:
        print(f"⚠️ [Independent Upgrade Warning]: {e}")

@admin_suppliers.route('/admin/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    # تشغيل الفحص الذاتي والترقية فوراً عند طلب الصفحة لضمان عدم حدوث خطأ UndefinedColumn
    auto_upgrade_supplier_table()

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

    next_id_num = 1
    try:
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        if last_supplier:
            next_id_num = last_supplier.id + 1
    except Exception as e:
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
