# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.utils.orders_engine import OrdersEngine
import logging

# تعريف الـ Blueprint
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض لوحة التحكم الخاصة بالطلبات"""
    try:
        # تعريف الأعمدة التي ستظهر في الجدول
        columns = [
            {'label': 'رقم الطلب', 'key': 'order_id_qumra'},
            {'label': 'العميل', 'key': 'customer_name'},
            {'label': 'الإجمالي', 'key': 'total'},
            {'label': 'الحالة', 'key': 'status'},
            {'label': 'التاريخ', 'key': 'created_at'}
        ]
        
        engine = OrdersEngine()
        # جلب الطلبات (تأكد من وجود دالة get_all_orders أو ما يشابهها في OrdersEngine)
        orders = engine.get_all_orders()
        
        return render_template(
            'admin/orders_dashboard.html', 
            orders=orders, 
            columns=columns
        )
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        return "خطأ في تحميل الصفحة", 500

@orders_bp.route('/sync-orders', methods=['POST'])
@login_required
def sync_orders():
    """مسار مزامنة الطلبات من قمرة"""
    try:
        engine = OrdersEngine()
        success = engine.sync_orders_from_source()
        return jsonify({'success': success, 'message': 'تمت المزامنة بنجاح'})
    except Exception as e:
        logging.error(f"Sync error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@orders_bp.route('/update-order-status', methods=['POST'])
@login_required
def update_order_status():
    """تحديث حالة الطلب"""
    try:
        data = request.get_json()
        order_id = data.get('orderId')
        new_status = data.get('value')
        
        engine = OrdersEngine()
        success = engine.update_status(order_id, new_status)
        
        return jsonify({'success': success})
    except Exception as e:
        logging.error(f"Update status error: {str(e)}")
        return jsonify({'success': False, 'message': 'فشل التحديث'}), 500
