# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from apps import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial # استيراد الموديل المالي
from apps.orders.services import OrderService

# تعريف الـ Blueprint
orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    """
    عرض لوحة تحكم الطلبات مع الإحصائيات الحية
    يتم الربط بين الطلبات والمالية لجلب البيانات كاملة
    """
    
    # 1. حساب الإحصائيات (Stats)
    # نستخدم الموديل المالي OrderFinancial لحساب إجمالي المبيعات
    total_sales = db.session.query(db.func.sum(OrderFinancial.amount)).scalar() or 0
    
    stats = {
        'cancelled': Order.query.filter_by(status='cancelled').count(),
        'completed': Order.query.filter_by(status='completed').count(),
        'total_sales': total_sales
    }
    
    # 2. جلب قائمة الطلبات مع بياناتها المالية (Join)
    # النتيجة ستكون قائمة من (Order, OrderFinancial)
    items = db.session.query(Order, OrderFinancial)\
        .join(OrderFinancial, Order.id == OrderFinancial.order_id)\
        .order_by(Order.id.desc()).all()
    
    return render_template('admin/orders_dashboard.html', stats=stats, items=items)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """
    دالة تشغيل المزامنة اليدوية
    """
    # استدعاء المصنع (تأكد من تمرير المعرفات الصحيحة)
    success = OrderService.fetch_and_sync_orders(api_key="YOUR_API_KEY", supplier_id=1)
    
    if success:
        flash("تمت المزامنة وتحديث البيانات بنجاح", "success")
    else:
        flash("حدث خطأ أثناء المزامنة، يرجى مراجعة سجلات الخطأ", "danger")
        
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/view-order/<int:order_id>')
@login_required
def view_order(order_id):
    """عرض تفاصيل طلب محدد"""
    # جلب الطلب مع بياناته المالية
    order_data = db.session.query(Order, OrderFinancial)\
        .filter(Order.id == order_id)\
        .join(OrderFinancial, Order.id == OrderFinancial.order_id).first_or_404()
        
    return render_template('admin/order_details.html', order=order_data[0], financial=order_data[1])
