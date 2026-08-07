# coding: utf-8
# 📂 apps/admin_orders/routes/items_controller.py

from flask import Blueprint, request, jsonify, render_template

items_bp = Blueprint('items_bp', __name__)

# 1. مسار جلب وعرض عناصر الطلب داخل الجدول
@items_bp.route('/admin/orders/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    try:
        from apps.models.order_items_db import OrderItem
        items = OrderItem.query.filter_by(order_id=order_id).all()
        return render_template('admin/order/_items_table_card.html', items=items, order_id=order_id)
    except Exception as e:
        return f'<div class="alert alert-danger">خطأ في تحميل العناصر: {str(e)}</div>', 500

# 2. مسار تعيين المورد للعنصر
@items_bp.route('/admin/orders/<int:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json()
        supplier_id = data.get('supplier_id')
        
        if supplier_id == "":
            supplier_id = None
        else:
            supplier_id = int(supplier_id) if supplier_id else None

        # منطق التحديث في قاعدة البيانات هنا...
        from apps.models.order_items_db import OrderItem
        from apps.extensions import db
        
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if item:
            item.supplier_id = supplier_id
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم تعيين المورد بنجاح',
            'supplier_name': 'اسم المورد'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
