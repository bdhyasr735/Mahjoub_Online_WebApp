# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/dashboard_routes.py

from flask import Blueprint, render_template, abort, session, redirect
from flask_login import login_required, current_user
from sqlalchemy import func

from apps.models import db, Supplier, Order, SupplierWallet, OrderFinancial

# تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """دالة مساعدة لجلب المورد والمحفظة بأمان"""
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        return None
        
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if supplier:
        wallet = db.session.execute(
            db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
        ).unique().scalar_one_or_none()
        supplier.wallet = wallet
        
    return supplier


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة التحكم الرئيسية للمورد"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    
    # عدد الطلبات قيد التنفيذ
    pending_orders_count = Order.query.filter_by(
        supplier_id=supplier.id, 
        status='pending'
    ).count()
    
    # إجمالي المبيعات (SAR فقط)
    total_sales = db.session.query(
        func.sum(OrderFinancial.total_paid_raw)
    ).join(
        Order, Order.id == OrderFinancial.order_id
    ).filter(
        Order.supplier_id == supplier.id,
        Order.status == 'completed'
    ).scalar() or 0
    
    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        pending_orders_count=pending_orders_count,
        total_sales=float(total_sales)
    )
