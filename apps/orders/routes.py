# coding: utf-8
# 📂 apps/orders/routes.py - النسخة السيادية المتوافقة مع القيادة المركزية

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

# 1. لوحة تحكم الطلبات مع الفلاتر
@orders_bp.route('/dashboard')
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    # الحصول على الفلاتر من الرابط
    status_payment = request.args.get('payment_status')
    status_shipping = request.args.get('shipping_status')
    
    query = ProcessedOrder.query
    
    if status_payment:
        query = query.filter_by(payment_status=status_payment)
    if status_shipping:
        query = query.filter_by(shipping_status=status_shipping)
        
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

# 3. تحديث الحالات (AJAX - لدعم القوائم المنسدلة في الجدول)
@orders_bp.route('/update-status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    data = request.get_json()
    order = ProcessedOrder.query.get_or_404(order_id)
    
    # تحديث الحقل بناءً على الطلب القادم من القائمة المنسدلة
    if 'payment_status' in data:
        order.payment_status = data['payment_status']
    if 'shipping_status' in data:
        order.shipping_status = data['shipping_status']
        
    db.session.commit()
    return jsonify({'status': 'success'})

# 4. مسار حذف الطلب (للإجراءات)
@orders_bp.route('/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash("تم حذف الطلب بنجاح", "info")
    return redirect(url_for('orders.orders_dashboard'))

# 5. عرض تفاصيل الطلب
@orders_bp.route('/process/<int:order_id>')
def process_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

# 6. تحميل الفاتورة (نموذجي)
@orders_bp.route('/download-invoice/<int:order_id>')
def download_invoice(order_id):
    # هنا يتم استدعاء دالة توليد الـ PDF
    flash("جاري تجهيز الفاتورة للتحميل...", "info")
    return redirect(url_for('orders.orders_dashboard'))
