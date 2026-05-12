from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from models.supplier_db import db, Supplier

add_supplier_bp = Blueprint(
    'add_supplier', 
    __name__, 
    template_folder='templates' # يشير إلى مجلد templates داخل add_supplier
)

# تعديل المسار ليكون متوافقاً مع طلبك
@add_supplier_bp.route('/supplier/add', methods=['GET', 'POST'])
def save_supplier():
    if not session.get('is_authenticated'):
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        last_supplier = Supplier.query.order_by(Supplier.id.desc()).first()
        next_id_count = (last_supplier.id + 1) if last_supplier else 1
        
        # تصحيح مسار القالب ليكون داخل مجلد admin كما طلبت
        return render_template('admin/add_supplier.html', next_id=next_id_count)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        try:
            new_supplier = Supplier(
                username=data.get('username'),
                password=data.get('password'),
                trade_name=data.get('trade_name'),
                owner_name=data.get('owner_name'),
                phone=data.get('phone'),
                activity_type=data.get('activity_type'),
                province=data.get('province'),
                district=data.get('district'),
                address_detail=data.get('address_detail'),
                bank_name=data.get('bank_name'),
                bank_acc=data.get('bank_acc')
            )
            count = Supplier.query.count() + 1
            new_supplier.sovereign_id = f"SUP-MHA_963{count}"

            db.session.add(new_supplier)
            db.session.commit()

            if request.is_json:
                return jsonify({'status': 'success', 'message': f'تم التعميد بالرقم: {new_supplier.sovereign_id}'})
            
            flash(f'تم حفظ المورد {new_supplier.trade_name} بنجاح.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
