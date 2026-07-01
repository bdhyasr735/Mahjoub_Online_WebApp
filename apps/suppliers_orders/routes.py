# coding: utf-8
# 📂 apps/suppliers_orders/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order
# تم التصحيح: استيراد الموديل من الملف بالمفرد supplier_db
from apps.models.supplier_db import Supplier

suppliers_orders_bp = Blueprint('suppliers_orders', __name__, template_folder='templates')

@suppliers_orders_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الطلبات الخاصة بالموردين"""
    page = request.args.get('page', 1, type=int)
    supplier_id = request.args.get('supplier_id')
    
    # الربط مع جدول الموردين لجلب البيانات
    query = Order.query.join(Supplier)
    
    # التصفية حسب المورد إذا وُجد
    if supplier_id:
        query = query.filter(Order.supplier_id == supplier_id)
        
    # تفعيل نظام الصفحات (Pagination)
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    # دعم طلبات الـ AJAX لتحديث الجدول ديناميكياً
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_supplier_table.html', pagination=pagination)
        
    return render_template('admin/suppliers_orders_dashboard.html', pagination=pagination)
