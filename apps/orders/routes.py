# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, jsonify
from apps.utils.orders_engine import OrdersEngine
import logging

logger = logging.getLogger(__name__)

# نحدد template_folder ليكون داخل مجلد الطلبات الجديد
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard', methods=['GET'])
def orders_dashboard():
    """عرض لوحة تحكم الطلبات المستقلة"""
    return render_template('admin/orders/orders_dashboard.html')

@orders_bp.route('/api/orders', methods=['GET'])
def api_orders():
    """جلب بيانات الطلبات من المحرك المتخصص"""
    try:
        engine = OrdersEngine()
        orders = engine.fetch_all_orders()
        return jsonify({
            "status": "success",
            "orders": orders
        })
    except Exception as e:
        logger.error(f"Error in api_orders: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "فشل في جلب بيانات الطلبات"
        }), 500
