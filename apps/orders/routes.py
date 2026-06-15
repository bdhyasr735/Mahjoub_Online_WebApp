# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.models.order_db import Order
from apps.utils.orders_engine import OrdersEngine
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/admin/orders', methods=['GET'])
@login_required
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/orders_dashboard.html', orders=pagination.items, pagination=pagination)

@orders_bp.route('/admin/orders/sync', methods=['POST'])
@login_required
def sync_orders():
    try:
        engine = OrdersEngine()
        count = engine.sync_orders_to_db()
        return jsonify({'success': True, 'message': f'تمت المزامنة، تم معالجة {count} طلب.'})
        
    except Exception as e:
        # هذا الجزء سيكشف الخطأ بوضوح في المتصفح وفي الـ Logs
        error_msg = f"فشل المزامنة: {str(e)}"
        logger.error(error_msg)
        return jsonify({'success': False, 'message': error_msg}), 500
