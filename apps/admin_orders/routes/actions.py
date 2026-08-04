# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.order_items_db import OrderItem

# تعريف الـ Blueprint الخاص بالإجراءات بنفس تسمية السكريبت
actions_bp = Blueprint('admin_order_actions', __name__, url_prefix='/admin/orders')

# خريطة لتحديث العنوان بناءً على الكود
STATUS_TITLES_MAP = {
    'pending': 'قيد الانتظار',
    'processing': 'قيد التجهيز',
    'shipped': 'تم الشحن',
    'delivered': 'تم التسليم',
    'completed': 'مكتمل',
    'cancelled': 'ملغي',
    'refunded': 'مسترجع'
}

@actions_bp.route('/<string:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """تحديث حالة الطلب (يستقبل JSON كما يرسله السكريبت)"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        new_status_code = data.get('status')
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.status_code = new_status_code
        # تحديث العنوان بناءً على الخريطة أو القيمة الافتراضية
        order.status_title = STATUS_TITLES_MAP.get(new_status_code, 'حالة غير معروفة')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث حالة الطلب بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500


@actions_bp.route('/<string:order_id>/payment-status', methods=['POST'])
@login_required
def update_payment_status(order_id):
    """تحديث حالة الدفع (isPaid)"""
    try:
        data = request.get_json()
        if not data or 'isPaid' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        is_paid = data.get('isPaid')
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.is_paid = bool(is_paid)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث حالة الدفع بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500


@actions_bp.route('/<string:order_id>/items/supplier', methods=['POST'])
@login_required
def update_item_supplier(order_id):
    """تحديث المورد لعنصر داخل الطلب (للدعم المستقبلي)"""
    try:
        data = request.get_json()
        if not data or 'item_id' not in data or 'supplier_id' not in data:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400

        item_id = data.get('item_id')
        supplier_id = data.get('supplier_id')

        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        # البحث عن العنصر داخل هذا الطلب فقط
        item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        if not item:
            return jsonify({'success': False, 'message': 'العنصر غير موجود في هذا الطلب'}), 404

        item.supplier_id = supplier_id if supplier_id else None
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث مورد العنصر بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500


@actions_bp.route('/delete/<string:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """حذف طلب من لوحة الإدارة (يعيد JSON ليكون متوافقاً)"""
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
            
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الطلب بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'فشل حذف الطلب: {str(e)}'}), 500
