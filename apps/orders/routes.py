# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort, current_app
from flask_login import login_required
from datetime import datetime
from sqlalchemy import func
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.models.supplier_db import Supplier
from apps.orders.services import OrderService
from apps.api.sync_engine import SyncEngine 

orders_bp = Blueprint('orders', __name__, template_folder='templates')

def admin_required():
    if session.get('user_type') != 'admin':
        abort(403)

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    admin_required()
    
    can_add_order = 'orders.add_new_order' in current_app.view_functions
    can_sync = 'orders.sync_all' in current_app.view_functions
    
    total_sales = db.session.query(func.sum(OrderFinancial.total_paid_raw)).scalar() or 0
    completed_count = Order.query.filter_by(status='completed').count()
    cancelled_count = Order.query.filter_by(status='cancelled').count()
    
    stats = {
        'total_sales': total_sales,
        'completed': completed_count,
        'cancelled': cancelled_count
    }
    
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(Order, OrderFinancial)\
        .outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)\
        .order_by(Order.id.desc())\
        .paginate(page=page, per_page=20)
    
    return render_template('admin/orders_dashboard.html', 
                           pagination=pagination, 
                           stats=stats,
                           can_add_order=can_add_order,
                           can_sync=can_sync)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """المسار المسؤول عن تشغيل المزامنة اليدوية مع قمرة"""
    admin_required()
    
    # تنفيذ المزامنة اليدوية
    # تأكد من أن هذه الدالة موجودة في SyncEngine وتقوم بجلب الطلبات
    sync_result = SyncEngine.run_manual_sync() 
    
    if sync_result:
        flash("تمت عملية المزامنة بنجاح وجلب الطلبات الجديدة.", "success")
    else:
        flash("حدث خطأ أثناء المزامنة، يرجى مراجعة سجلات الأخطاء.", "danger")
        
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_new_order():
    admin_required()
    if request.method == 'POST':
        order_id = str(int(datetime.utcnow().timestamp()))
        supplier_id_input = request.form.get('supplier_id', type=int)
        total_price = float(request.form.get('total_price', 0))
        
        supplier = Supplier.query.get(supplier_id_input)
        if not supplier:
            flash("خطأ: المتجر غير موجود.", "danger")
            return redirect(url_for('orders.add_new_order'))
        
        new_order = Order(
            id=order_id,
            order_id_display=f"MHJ-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            customer_name=request.form.get('customer_name'),
            customer_phone=request.form.get('customer_phone'),
            supplier_id=supplier_id_input, 
            total_price=total_price,
            status='pending'
        )
        db.session.add(new_order)
        
        new_financial = OrderFinancial(
            order_id=order_id,
            supplier_id=supplier_id_input,
            currency='SAR',
            settlement_status='pending',
            shipping_fees=0.0
        )
        
        new_financial.total_paid = total_price
        new_financial.supplier_cost = 0.0
        new_financial.mahjoub_commission = 0.0
        
        db.session.add(new_financial)
        db.session.commit()
        flash("تم إضافة الطلب وتسجيله في النظام بنجاح.", "success")
        return redirect(url_for('orders.dashboard'))
    
    suppliers = Supplier.query.all()
    return render_template('admin/add_order.html', suppliers=suppliers)

@orders_bp.route('/complete-order/<string:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    admin_required()
    if OrderService.complete_order_and_settle(order_id):
        flash("تمت تسوية الطلب وتحويل الأرباح بنجاح.", "success")
    else:
        flash("فشل التسوية: ربما تم تسوية الطلب مسبقاً.", "danger")
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders_bp.route('/view-order/<string:order_id>') 
@login_required
def view_order(order_id):
    admin_required()
    order, financial = OrderService.get_order_details(order_id)
    if not order:
        abort(404)
    return render_template('admin/order_details.html', order=order, financial=financial)
