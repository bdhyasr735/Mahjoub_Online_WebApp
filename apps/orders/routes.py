# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required
from datetime import datetime
from sqlalchemy import func  # تم إضافة الاستيراد المطلوب للإحصائيات[cite: 9]
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
    
    # 1. حساب الإحصائيات لعرضها في البطاقات العلوية[cite: 5]
    total_sales = db.session.query(func.sum(OrderFinancial.total_paid)).scalar() or 0
    completed_count = Order.query.filter_by(status='completed').count()
    cancelled_count = Order.query.filter_by(status='cancelled').count()
    
    stats = {
        'total_sales': total_sales,
        'completed': completed_count,
        'cancelled': cancelled_count
    }
    
    # 2. إعداد الترقيم وجلب البيانات المترابطة[cite: 2]
    page = request.args.get('page', 1, type=int)
    
    # جلب الطلبات والبيانات المالية معاً ليتوافق مع حلقة التكرار في _table.html[cite: 2, 9]
    pagination = db.session.query(Order, OrderFinancial)\
        .outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)\
        .order_by(Order.id.desc())\
        .paginate(page=page, per_page=20)
    
    # 3. تمرير المتغيرات المطلوبة للقالب[cite: 5]
    return render_template('admin/orders_dashboard.html', 
                           pagination=pagination, 
                           stats=stats)

@orders_bp.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_new_order():
    admin_required()
    if request.method == 'POST':
        order_id = str(int(datetime.utcnow().timestamp()))
        supplier_id_input = request.form.get('supplier_id', type=int)
        
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
            total_price=float(request.form.get('total_price', 0)),
            status='pending'
        )
        db.session.add(new_order)
        
        new_financial = OrderFinancial(
            order_id=order_id,
            supplier_id=supplier_id_input,
            total_paid=float(request.form.get('total_price', 0)),
            total_paid_raw=float(request.form.get('total_price', 0)),
            currency='SAR'
        )
        db.session.add(new_financial)
        
        db.session.commit()
        flash("تم إضافة الطلب بنجاح.", "success")
        return redirect(url_for('orders.dashboard'))
    
    return render_template('admin/add_order.html')

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
