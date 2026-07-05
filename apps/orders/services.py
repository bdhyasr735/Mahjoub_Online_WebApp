# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.orders.services import OrderService # استيراد الخدمة الجديدة
from apps.api.sync_engine import SyncEngine

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    # استخدام الخدمة لجلب البيانات
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    
    pagination = OrderService.get_paginated_orders(page, 20, search_query, status)
    stats = OrderService.get_dashboard_stats()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_table.html', pagination=pagination)
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, stats=stats)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    # منطق المزامنة يبقى هنا أو يمكن نقله لـ Service لاحقاً
    if SyncEngine.fetch_and_sync_order():
        flash("تم تحديث الطلبات بنجاح.", "success")
    else:
        flash("حدث خطأ أثناء المزامنة.", "danger")
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/view-order/<int:order_id>') 
@login_required
def view_order(order_id):
    # استخدام الخدمة لجلب التفاصيل
    order_data = OrderService.get_order_details(order_id)
    return render_template('admin/order_details.html', order=order_data[0], financial=order_data[1])
