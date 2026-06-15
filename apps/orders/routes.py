# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.utils.orders_engine import OrdersEngine
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint باسم 'orders'
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
    """لوحة تحكم الطلبات"""
    try:
        # تعريف الأعمدة التي ستظهر في الجدول
        columns = [
            {'label': 'رقم الطلب', 'key': 'order_id_qumra'},
            {'label': 'العميل', 'key': 'customer_name'},
            {'label': 'الإجمالي', 'key': 'total'},
            {'label': 'حالة الطلب', 'key': 'status'},
            {'label': 'التاريخ', 'key': 'created_at'}
        ]
        
        engine = OrdersEngine()
        page = request.args.get('page', 1, type=int)
        pagination = engine.get_paginated_orders(page=page)
        
        return render_template(
            'admin/orders_dashboard.html', 
            orders=pagination.items, 
            pagination=pagination,
            columns=columns
        )
    except Exception as e:
        logger.exception("Error loading orders dashboard")
        return f"حدث خطأ أثناء تحميل لوحة الطلبات: {str(e)}", 500

@orders_bp.route('/sync-orders', methods=['POST'])
@login_required
def sync_orders():
    """مزامنة الطلبات - مسار فريد لمنع التضارب"""
    try:
        engine = OrdersEngine()
        count = engine.sync_orders_from_source()
        return jsonify({'success': True, 'message': f'تمت مزامنة {count} طلب بنجاح'})
    except Exception as e:
        logger.error(f"Error syncing orders: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل المزامنة'}), 500

@orders_bp.route('/update-status', methods=['POST'])
@login_required
def update_order_status():
    """تحديث حالة الطلب"""
    try:
        data = request.json
        order_id = data.get('orderId')
        new_status = data.get('value')
        
        engine = OrdersEngine()
        engine.update_status(order_id, new_status)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
