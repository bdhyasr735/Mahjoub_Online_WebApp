# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder
from apps.api.sync_engine import SyncEngine
import logging

orders_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='templates')
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات مع التنظيف الذكي للبيانات
@orders_bp.route('/dashboard')
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    payment_status = request.args.get('payment_status', '')
    fulfillment_status = request.args.get('fulfillment_status', '')
    
    query = ProcessedOrder.query
    
    # حساب الإحصائيات
    all_orders = ProcessedOrder.query.all()
    total_sales = sum([float(order.total_price or 0) for order in all_orders])
    
    completed_count = ProcessedOrder.query.filter_by(fulfillment_status='fulfilled').count()
    cancelled_count = ProcessedOrder.query.filter_by(order_status='cancelled').count()
    
    # الفلترة والبحث
    if search:
        query = query.filter((ProcessedOrder.order_id.contains(search)) | (ProcessedOrder.customer_name.contains(search)))
    
    if payment_status and payment_status != 'all':
        query = query.filter_by(financial_status=payment_status)
    if fulfillment_status and fulfillment_status != 'all':
        query = query.filter_by(fulfillment_status=fulfillment_status)
        
    pagination = query.order_by(ProcessedOrder.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # 💡 منطق التنظيف الذكي: تعويض None بـ "---"
    for order in pagination.items:
        if not order.customer_name: order.customer_name = "---"
        if not order.customer_phone: order.customer_phone = "---"
        if not order.shipping_city: order.shipping_city = "---"
        if not order.shipping_street: order.shipping_street = "---"
    
    return render_template('admin/orders_dashboard.html', 
                           pagination=pagination, 
                           stats={
                               'total_sales': total_sales, 
                               'completed': completed_count, 
                               'cancelled': cancelled_count
                           }, 
                           search=search, 
                           payment_status=payment_status, 
                           fulfillment_status=fulfillment_status)

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
        setattr(order, data['field'], data['value'])
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404

# 4. الإجراءات الإضافية
@orders_bp.route('/view/<order_id>')
def view_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    return render_template('admin/view_order.html', order=order)

@orders_bp.route('/download-invoice/<order_id>')
def download_invoice(order_id):
    flash(f"جاري تحضير فاتورة الطلب #{order_id}...", "info")
    return redirect(url_for('orders.orders_dashboard'))

@orders_bp.route('/delete-order/<order_id>', methods=['POST'])
def delete_order(order_id):
    order = ProcessedOrder.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404
