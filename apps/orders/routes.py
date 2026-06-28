# coding: utf-8
# 📂 apps/orders/routes.py

import os
import traceback # لاستخراج تفاصيل الخطأ البرمجي
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.orders.services import OrderService

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    all_financials = OrderFinancial.query.all()
    total_sales = sum(f.total_paid for f in all_financials)
    
    stats = {
        'cancelled': Order.query.filter_by(status='cancelled').count(),
        'completed': Order.query.filter_by(status='completed').count(),
        'total_sales': float(total_sales)
    }
    
    items = db.session.query(Order, OrderFinancial)\
        .join(OrderFinancial, Order.id == OrderFinancial.order_id)\
        .order_by(Order.id.desc()).all()
    
    return render_template('admin/orders_dashboard.html', stats=stats, items=items)

@orders_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """دالة المزامنة مع التقاط الأخطاء التفصيلي."""
    api_key = os.environ.get("QUMRA_API_KEY")
    
    if not api_key:
        flash("خطأ: مفتاح الـ API غير معرف في إعدادات النظام", "danger")
        return redirect(url_for('orders.dashboard'))

    try:
        # نقوم بتشغيل المزامنة
        success = OrderService.fetch_and_sync_orders(api_key=api_key, supplier_id=1)
        
        if success:
            flash("تمت المزامنة وتحديث البيانات بنجاح", "success")
        else:
            # إذا فشلت المزامنة، سنحاول جلب آخر رسالة خطأ من السجلات إذا أردت
            flash("فشلت المزامنة. يرجى التحقق من سجلات النظام (Logs) في Render.", "danger")
            
    except Exception as e:
        # هنا سنعرض الخطأ الحقيقي للمطور (أنت) في رسالة الـ Flash
        error_details = str(e)
        flash(f"حدث خطأ تقني: {error_details}", "danger")
        # طباعة الخطأ كاملاً في الـ Console الخاص بـ Render
        traceback.print_exc()
        
    return redirect(url_for('orders.dashboard'))

@orders_bp.route('/view-order/<string:order_id>') 
@login_required
def view_order(order_id):
    result = db.session.query(Order, OrderFinancial)\
        .filter(Order.id == order_id)\
        .join(OrderFinancial, Order.id == OrderFinancial.order_id).first_or_404()
        
    return render_template('admin/order_details.html', order=result[0], financial=result[1])
