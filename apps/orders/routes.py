# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from datetime import datetime
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.models.supplier_db import Supplier
from apps.orders.services import OrderService
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func

# تم توحيد اسم البلوبرينت إلى 'orders' ليطابق هيكل المجلد ويمنع تضارب التسجيل
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/orders_dashboard.html')

@orders_bp.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_new_order():
    if request.method == 'POST':
        order_id = str(int(datetime.utcnow().timestamp()))
        
        try:
            supplier_id_input = int(request.form.get('supplier_id'))
        except (ValueError, TypeError):
            flash("خطأ في بيانات المورد: يجب إدخال معرف رقمي صحيح.", "danger")
            return redirect(url_for('orders.add_new_order'))
        
        if not Supplier.query.get(supplier_id_input):
            flash("خطأ: المتجر غير موجود في النظام.", "danger")
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
    if OrderService.complete_order_and_settle(order_id):
        flash("تمت تسوية الطلب بنجاح.", "success")
    else:
        flash("فشل في تسوية الطلب.", "danger")
    # استخدام الاسم الموحد 'orders.view_order'
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders_bp.route('/view-order/<string:order_id>') 
@login_required
def view_order(order_id):
    order, financial = OrderService.get_order_details(order_id)
    if not order:
        return "الطلب غير موجود", 404
        
    return render_template('admin/order_details.html', order=order, financial=financial)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    # إضافة مسار المزامنة ليتوافق مع القالب
    SyncEngine.run_sync()
    flash("تمت عملية المزامنة بنجاح.", "success")
    return redirect(url_for('orders.dashboard'))
