# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user

# تعريف الـ Blueprint باسم 'orders'
# يجب أن يتطابق هذا الاسم مع ما هو موجود في registry.py (الروابط)
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    # استيراد محلي لتجنب Circular Import
    from apps.extensions import db
    from apps.models.orders_db import Order
    from apps.models.financials_db import OrderFinancial
    
    page = request.args.get('page', 1, type=int)
    # جلب البيانات مع الباجينيشن
    pagination = Order.query.outerjoin(OrderFinancial).paginate(page=page, per_page=20)
    
    # حساب الإحصائيات
    stats = {
        'total_sales': db.session.query(db.func.sum(OrderFinancial.total_paid)).scalar() or 0,
        'completed': Order.query.filter_by(status='completed').count(),
        'cancelled': Order.query.filter_by(status='cancelled').count()
    }
    
    return render_template(
        'admin/orders_dashboard.html', 
        pagination=pagination, 
        stats=stats,
        can_add_order=True, 
        can_sync=True
    )

@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_new_order():
    from apps.extensions import db
    from apps.models.supplier_db import Supplier
    from apps.models.orders_db import Order
    
    if request.method == 'POST':
        try:
            new_order = Order(
                customer_name=request.form.get('customer_name'),
                customer_phone=request.form.get('customer_phone'),
                supplier_id=request.form.get('supplier_id'),
                total_price=request.form.get('total_price'),
                status='pending'
            )
            db.session.add(new_order)
            db.session.commit()
            flash("تم إضافة الطلب بنجاح", "success")
            # الربط هنا باسم الـ Blueprint المعتمد 'orders'
            return redirect(url_for('orders.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"خطأ في حفظ الطلب: {e}", "danger")
            
    suppliers = Supplier.query.all()
    return render_template('admin/add_order.html', suppliers=suppliers)

@orders_bp.route('/sync', methods=['POST'])
@login_required
def sync_all():
    # منطق المزامنة
    flash("تمت المزامنة بنجاح", "info")
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/view/<int:order_id>')
@login_required
def view_order(order_id):
    from apps.models.orders_db import Order
    order = Order.query.get_or_404(order_id)
    return render_template('admin/view_order.html', order=order)
