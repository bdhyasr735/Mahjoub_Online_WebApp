# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import request, jsonify
from apps.admin_orders.routes import admin_orders_bp
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.order_items_db import OrderItem

@admin_orders_bp.route('/<string:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """تحديث حالة الطلب العامة عبر AJAX"""
    data = request.get_json() or {}
    new_status = data.get('status')
    
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        order.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث حالة الطلب بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_orders_bp.route('/<string:order_id>/payment-status', methods=['POST'])
def update_payment_status(order_id):
    """تحديث الحالة المالية (الدفع) عبر AJAX"""
    data = request.get_json() or {}
    is_paid = data.get('isPaid')
    
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        order.is_paid = is_paid
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث الحالة المالية بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_orders_bp.route('/<string:order_id>/items/supplier', methods=['POST'])
def update_item_supplier(order_id):
    """ربط بند معين داخل الطلب بمورد محلي عبر AJAX"""
    data = request.get_json() or {}
    item_id = data.get('item_id')
    supplier_id = data.get('supplier_id')
    
    try:
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if not item:
            return jsonify({'success': False, 'message': 'عنصر الطلب غير موجود'}), 404
            
        item.supplier_id = int(supplier_id) if supplier_id else None
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تعيين المورد المحلي للبند بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
