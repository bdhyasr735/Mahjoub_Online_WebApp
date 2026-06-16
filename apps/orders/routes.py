# 📂 apps/orders/routes.py
from flask import Blueprint, render_template
from flask_login import login_required
from apps.utils.orders_engine import get_pending_orders

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/pending', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض الطلبات المعلقة مباشرة من قمرة"""
    orders = get_pending_orders()
    return render_template('admin/orders_dashboard.html', orders=orders)
