# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from datetime import datetime
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.orders.services import OrderService  # الخدمة التي تحتوي منطق التسوية
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func

# تعريف الـ Blueprint باسم 'orders'
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الطلبات - محسنة للأداء العالي."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = db.session.query(Order, OrderFinancial).outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)
    
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(Order.order_id_display.ilike(f'%{q}%') | Order.customer_name.ilike(f'%{q}%'))
    
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Order.status == status)
        
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
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
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_table.html', pagination=pagination)
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, stats=stats)

@orders_bp.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_new_order():
    """إضافة طلب جديد يدوياً للنظام السيادي."""
    if request.method == 'POST':
        # إنشاء معرف فريد للطلب (Unix Timestamp)
        order_id = str(int(datetime.utcnow().timestamp()))
        
        new_order = Order(
            id=order_id,
            order_id_display=f"MHJ-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            customer_name=request.form.get('customer_name'),
            customer_phone=request.form.get('customer_phone'),
            supplier_id=request.form.get('supplier_id'),
            total_price=float(request.form.get('total_price', 0)),
            status='pending'
        )
        db.session.add(new_order)
        
        # إنشاء سجل مالي افتراضي مرتبط بالطلب
        new_financial = OrderFinancial(
            order_id=order_id,
            supplier_id=int(request.form.get('supplier_id')),
            total_paid=float(request.form.get('total_price', 0)),
            currency='SAR'
        )
        db.session.add(new_financial)
        
        db.session.commit()
        flash("تم إضافة الطلب والمركز المالي بنجاح.", "success")
        return redirect(url_for('orders.dashboard'))
    
    return render_template('admin/add_order.html')

@orders_bp.route('/complete-order/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    """تسوية الطلب مالياً وتحديث المحفظة تلقائياً."""
    if OrderService.complete_order_and_settle(order_id):
        flash("تمت تسوية الطلب بنجاح وإضافة الرصيد للمحفظة.", "success")
    else:
        flash("فشل في تسوية الطلب أو أن الطلب مسوى مسبقاً.", "danger")
    return redirect(url_for('orders.view_order', order_id=order_id))

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
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/view-order/<int:order_id>') 
@login_required
def view_order(order_id):
    order, financial = OrderService.get_order_details(order_id)
    if not order:
        return "الطلب غير موجود", 404
        
    return render_template('admin/order_details.html', order=order, financial=financial)
