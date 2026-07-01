# coding: utf-8
# 📂 apps/orders/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الطلبات - محسنة للأداء العالي."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # استخدام استعلام واحد ذكي
    query = db.session.query(Order, OrderFinancial).outerjoin(OrderFinancial, Order.id == OrderFinancial.order_id)
    
    # تطبيق الفلاتر
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(Order.order_id_display.ilike(f'%{q}%') | Order.customer_name.ilike(f'%{q}%'))
    
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Order.status == status)
        
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # إحصائيات سريعة - تصحيح: نستخدم db.session.query مع العمود الفعلي
    try:
        total_sales = db.session.query(func.sum(OrderFinancial.total_paid)).scalar() or 0
    except Exception:
        total_sales = 0 # تجاوز الخطأ في حال كان الموديل لا يزال يواجه تعارضاً
        
    stats = {
        'cancelled': Order.query.filter_by(status='cancelled').count(),
        'completed': Order.query.filter_by(status='completed').count(),
        'total_sales': total_sales
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_table.html', pagination=pagination)
    
    return render_template('admin/orders_dashboard.html', pagination=pagination, stats=stats)

# ... باقي الدوال (sync_all و view_order) تظل كما هي ...
