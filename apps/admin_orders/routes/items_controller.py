# coding: utf-8
from flask import Blueprint, request, jsonify, render_template, current_app
from apps.models.order_items_db import OrderItem
from apps.models.supplier_db import Supplier
from apps.extensions import db

items_bp = Blueprint('items_bp', __name__)

@items_bp.route('/admin/orders/<string:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    try:
        items_list = OrderItem.query.filter_by(order_id=order_id).all()
        all_suppliers = Supplier.query.all()
        return render_template(
            'admin/order/_items_table_card.html', 
            items_list=items_list, 
            all_suppliers=all_suppliers,
            order_id=order_id
        )
    except Exception as e:
        return f'<div class="alert alert-danger">خطأ: {str(e)}</div>', 500

@items_bp.route('/admin/orders/<string:order_id>/item/<int:item_id>/assign-supplier', methods=['POST'])
def assign_supplier(order_id, item_id):
    try:
        data = request.get_json()
        s_id = data.get('supplier_id')
        supplier_id = int(s_id) if s_id else None
        
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if item:
            item.supplier_id = supplier_id
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم التحديث'})
        return jsonify({'success': False, 'message': 'لم يتم العثور على العنصر'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
