# coding: utf-8
# 📂 apps/orders/routes.py - النسخة السيادية النهائية للقيادة المركزية

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder
from apps.api.sync_engine import SyncEngine
import logging

orders_bp = Blueprint(
    'orders', 
    __name__, 
    url_prefix='/orders', 
    template_folder='templates'
)
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات (مع دعم البحث والفلاتر والترقيم)
@orders_bp.route('/dashboard')
def orders_dashboard():
    # الحصول على البارامترات من الرابط
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    payment_status = request.args.get('payment_status', '')
    fulfillment_status = request.args.get('fulfillment_status', '')
    
    # بناء الاستعلام الأساسي
    query = ProcessedOrder.query
    
    # تطبيق البحث (بحث في رقم الطلب أو اسم العميل)
    if search:
        query = query.filter(
            (ProcessedOrder.order_id.contains(search)) | 
            (ProcessedOrder.customer_name.contains(search))
        )
    
    # تطبيق الفلاتر
    if payment_status:
        query = query.filter_by(financial_status=payment_status)
    if fulfillment_status:
        query = query.filter_by(fulfillment_status=fulfillment_status)
        
    # الترتيب والترقيم (10 طلبات في الصفحة)
    pagination = query.order_by(ProcessedOrder.created_at_local.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/orders_dashboard.html', pagination=pagination)

# 2. المزامنة الشاملة
@orders_bp.route('/sync-all', methods=['POST'])
def sync_all():
    try:
        SyncEngine.fetch_and_sync_order()
        flash("تمت مزامنة البيانات من قمرة بنجاح", "success")
    except Exception as e:
        logger.error(f"Sync error: {e}")
        flash("حدث خطأ أثناء المزامنة", "danger")
    return redirect(url_for('orders.orders_dashboard'))

# 3. تحديث الحالات (AJAX)
@orders_bp.route('/update-order-field/<string:order_id>', methods=['POST'])
def update_order_field(order_id):
    data = request.get_json()
    order = ProcessedOrder.query.get_or_404(order_id)
    
    field = data.get('field')
    value = data.get('value')
    
    if field in ['financial_status', 'fulfillment_status']:
        setattr(order, field, value)
        db.session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Invalid field'}), 400

# 4. مسار حذف الطلب
@orders_bp.route('/delete/<string:order_id>', methods=['POST'])
def delete_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash("تم حذف الطلب بنجاح", "info")
    return redirect(url_for('orders.orders_dashboard'))

# 5. عرض تفاصيل الطلب
@orders_bp.route('/process/<string:order_id>')
def process_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

# 6. تحميل الفاتورة
@orders_bp.route('/download-invoice/<string:order_id>')
def download_invoice(order_id):
    flash("جاري تجهيز الفاتورة للتحميل...", "info")
    return redirect(url_for('orders.orders_dashboard'))
