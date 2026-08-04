# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint, render_template, abort
from flask_login import login_required
from apps.models.orders_db import Order

# تعريف الـ Blueprint الخاص بإدارة الطلبات
admin_orders_bp = Blueprint(
    'admin_orders', 
    __name__, 
    template_folder='../templates', 
    url_prefix='/admin/orders'
)

@admin_orders_bp.route('/')
@login_required
def list_orders():
    """عرض قائمة الطلبات في لوحة الإدارة"""
    try:
        orders = Order.query.all()
    except Exception as e:
        orders = []
        print(جخطأ في جلب الطلبات: {e})
        
    return render_template('admin/admin_orders.html', orders=orders)

@admin_orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """عرض تفاصيل طلب محدد"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/admin_order_detail.html', order=order)
