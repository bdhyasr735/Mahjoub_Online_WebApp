# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from datetime import datetime
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.orders.services import OrderService
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func

orders_bp = Blueprint('orders', __name__, template_folder='templates')

# ... (دالة dashboard تبقى كما هي) ...

@orders_bp.route('/add-order', methods=['GET', 'POST'])
@login_required
def add_new_order():
    if request.method == 'POST':
        # المعرف هنا نصي كما حددناه سابقاً
        order_id = str(int(datetime.utcnow().timestamp()))
        
        # تحويل supplier_id إلى Integer لأن الموديلات المحدثة تتوقع Integer
        try:
            supplier_id_input = int(request.form.get('supplier_id'))
        except (ValueError, TypeError):
            flash("خطأ في بيانات المورد.", "danger")
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
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders_bp.route('/view-order/<string:order_id>') 
@login_required
def view_order(order_id):
    order, financial = OrderService.get_order_details(order_id)
    if not order:
        return "الطلب غير موجود", 404
        
    return render_template('admin/order_details.html', order=order, financial=financial)

# ... (باقي الدوال تبقى كما هي) ...
