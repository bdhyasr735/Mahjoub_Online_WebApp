# coding: utf-8
# 📂 apps/orders/routes.py - المحرك السيادي لمعالجة الطلبات (نسخة أداء عالٍ)

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
# تم تحديث الاستيراد من ProcessedOrder إلى Order
from apps.models import Order 
from apps.api.sync_engine import SyncEngine
from sqlalchemy import func
import logging

orders_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='templates')
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات
@orders_bp.route('/dashboard')
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # تم تحديث الاستعلام ليستخدم Order بدلاً من ProcessedOrder
    stats = db.session.query(
        func.sum(Order.total_price).label('total_sales'),
        func.count(Order.id).filter(Order.order_status == 'delivered').label('completed'),
        func.count(Order.id).filter(Order.order_status == 'cancelled').label('cancelled')
    ).first()
    
    # بناء استعلام البحث
    query = Order.query.order_by(Order.id.desc())
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Order.order_id.ilike(search_filter)) | 
            (Order.customer_name.ilike(search_filter))
        )
    
    # التقسيم (Pagination)
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/orders_dashboard.html', 
                           items=pagination.items,
                           total_pages=pagination.pages,
                           current_page=page,
                           stats={
                               'total_sales': stats.total_sales or 0, 
                               'completed': stats.completed or 0, 
                               'cancelled': stats.cancelled or 0
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
    order = Order.query.get(order_id) # تحديث للكلاس Order
    if order and hasattr(order, data.get('field')):
        try:
            setattr(order, data['field'], data['value'])
            db.session.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error updating field: {e}")
            return jsonify({'status': 'error', 'message': 'فشل تحديث البيانات'}), 500
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود أو الحقل غير مسموح'}), 404

# 4. حذف طلب
@orders_bp.route('/delete-order/<order_id>', methods=['POST'])
def delete_order(order_id):
    order = Order.query.get(order_id) # تحديث للكلاس Order
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'الطلب غير موجود'}), 404
