# coding: utf-8
# 📂 apps/admin_orders/routes/items_controller.py

from flask import Blueprint, request, jsonify, render_template, current_app
from apps.models.order_items_db import OrderItem
from apps.models.supplier_db import Supplier
from apps.extensions import db

items_bp = Blueprint('items_bp', __name__)

@items_bp.route('/admin/orders/<string:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    try:
        items_list = OrderItem.query.filter_by(order_id=order_id).all()
        # ✅ تعديل اسم المتغير ليكون 'suppliers' ليتطابق مع القالب المحدث
        suppliers = Supplier.query.all()
        return render_template(
            'admin/order/_items_table_card.html', 
            items_list=items_list, 
            suppliers=suppliers,
            order_id=order_id
        )
    except Exception as e:
        current_app.logger.error(f"Error loading items: {str(e)}")
        return f'<div class="alert alert-danger m-3">خطأ في تحميل العناصر: {str(e)}</div>', 500

@items_bp.route('/admin/orders/<string:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json() or {}
        s_id = data.get('supplier_id')
        
        # ✅ تحسين: التعامل مع القيم الفارغة بأمان قبل التحويل إلى int
        if s_id is not None and s_id != '':
            supplier_id = int(s_id)
        else:
            supplier_id = None
        
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if item:
            item.supplier_id = supplier_id
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم تعيين المورد بنجاح'})
        return jsonify({'success': False, 'message': 'العنصر غير موجود'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
