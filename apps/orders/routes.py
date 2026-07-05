# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func

# تعريف الـ Blueprint باسم 'orders' لضمان توافق url_for
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def index():
    """لوحة تحكم الطلبات - محسنة للأداء العالي."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 1. استخدام استعلام واحد ذكي لجلب البيانات والربط
    query = db.session.query(Order, OrderFinancial).outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)
    
    # 2. تطبيق الفلاتر
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(Order.order_id_display.ilike(f'%{q}%') | Order.customer_name.ilike(f'%{q}%'))
    
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Order.status == status)
        
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 3. إحصائيات سريعة
    try:
        total_sales = db.session.query(func.sum(OrderFinancial.total_paid_raw)).scalar() or 0
    except Exception as e:
        print(f"⚠️ Error calculating stats: {e}")
        total_sales = 0 
        
    stats = {
        'cancelled': Order.query.filter_by(status='cancelled').count(),
        'completed': Order.query.filter_by(status='completed').count(),
        'total_sales': float(total_sales) 
    }
    
    # دعم طلبات الـ AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_table.html', pagination=pagination)
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, stats=stats)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    try:
        if SyncEngine.fetch_and_sync_order():
            flash("تم تحديث الطلبات بنجاح.", "success")
        else:
            flash("حدث خطأ أثناء المزامنة.", "danger")
    except Exception as e:
        flash(f"خطأ تقني: {str(e)}", "danger")
    return redirect(url_for('orders.index'))

@orders_bp.route('/view-order/<int:order_id>') 
@login_required
def view_order(order_id):
    result = db.session.query(Order, OrderFinancial)\
        .outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)\
        .filter(Order.id == order_id).first_or_404()
        
    return render_template('admin/order_details.html', order=result[0], financial=result[1])
