# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models import ProcessedOrder
from apps.api.sync_engine import SyncEngine
import logging

orders_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='templates')
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات مع التنظيف الذكي
@orders_bp.route('/dashboard')
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # استرجاع جميع الطلبات للعمليات الحسابية
    all_orders = ProcessedOrder.query.all()
    
    # حساب الإحصائيات (بناءً على الـ Properties المفكوكة في الموديل)
    total_sales = sum([float(order.total_price or 0) for order in all_orders])
    
    # ملاحظة: تم تحديث الحالة لتطابق ما يتم جلبه من API
    completed_count = sum(1 for o in all_orders if o.order_status == 'delivered')
    cancelled_count = sum(1 for o in all_orders if o.order_status == 'cancelled')
    
    # البحث
    query = ProcessedOrder.query.order_by(ProcessedOrder.id.desc())
    items = query.all()
    
    if search:
        items = [o for o in items if search.lower() in str(o.order_id).lower() or 
                                     search.lower() in o.customer_name.lower()]
    
    # التقسيم (Pagination) يدوي
    start = (page - 1) * 10
    end = start + 10
    pagination_items = items[start:end]
    
    # التنظيف الذكي للعرض (تعويض القيم الفارغة)
    for order in pagination_items:
        if not order.customer_name: order.customer_name = "---"
        if not order.customer_phone: order.customer_phone = "---"
        if not order.shipping_city: order.shipping_city = "---"
    
    return render_template('admin/orders_dashboard.html', 
                           items=pagination_items,
                           total_pages=(len(items)//10) + 1,
                           current_page=page,
                           stats={
                               'total_sales': total_sales, 
                               'completed': completed_count, 
                               'cancelled': cancelled_count
                           }, 
                           search=search)

# 2. المزامنة
@orders_bp.route('/sync-all', methods=['POST'])
def sync_all():
    if SyncEngine.fetch_and_sync_order():
        flash("✅ تمت المزامنة بنجاح!", "success")
    else:
        flash("⚠️ فشلت المزامنة، يرجى مراجعة سجلات الأخطاء.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

# 3. تحديث الحقول لحظياً (AJAX)
@orders_bp.route('/update-order-field/<order_id>', methods=['POST'])
def update_order_field(order_id):
    data = request.json
    order = ProcessedOrder.query.get(order_id)
    if order:
        # الموديل يتكفل بالتشفير تلقائياً عبر الـ setter
        setattr(order, data['field'], data['value'])
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404

# 4. حذف طلب
@orders_bp.route('/delete-order/<order_id>', methods=['POST'])
def delete_order(order_id):
    order = ProcessedOrder.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404
