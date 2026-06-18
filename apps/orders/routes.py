# coding: utf-8
# 📂 apps/orders/routes.py - التحكم في مسارات الطلبات والمزامنة

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder, OrderItem
from apps.api.sync_engine import SyncEngine
import logging

# تعريف الـ Blueprint
orders_bp = Blueprint('orders', __name__, url_prefix='/orders')
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات مع الترقيم
@orders_bp.route('/dashboard')
def orders_dashboard():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = ProcessedOrder.query.order_by(ProcessedOrder.created_at_local.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        # تم تعديل المسار ليطابق موقع الملف الفعلي: apps/orders/templates/admin/orders_dashboard.html
        return render_template('admin/orders_dashboard.html', pagination=pagination)
    except Exception as e:
        logger.error(f"Dashboard Error: {e}")
        return f"حدث خطأ أثناء تحميل لوحة التحكم: {str(e)}", 500

# 2. المزامنة الشاملة
@orders_bp.route('/sync-all', methods=['POST'])
def sync_all():
    try:
        if SyncEngine.fetch_and_sync_order():
            flash("تمت مزامنة الطلبات بنجاح.", "success")
        else:
            flash("لم يتم العثور على طلبات جديدة.", "warning")
    except Exception as e:
        logger.error(f"Sync error: {e}")
        flash("حدث خطأ أثناء المزامنة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

# 3. تحديث الحالات ديناميكياً
@orders_bp.route('/update-order-field/<string:order_id>', methods=['POST'])
def update_order_field(order_id):
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    order = ProcessedOrder.query.get_or_404(order_id)
    try:
        if hasattr(order, field):
            setattr(order, field, value)
            db.session.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
    return jsonify({'status': 'error'}), 400

# 4. تحديث المورد المحلي
@orders_bp.route('/update-supplier/<string:order_id>', methods=['POST'])
def update_supplier(order_id):
    data = request.get_json()
    supplier_name = data.get('supplier_name')
    order = ProcessedOrder.query.get_or_404(order_id)
    order.supplier_name = supplier_name
    try:
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error'}), 400

# 5. عرض ومعالجة الطلب التفصيلي
@orders_bp.route('/process/<string:order_id>')
def process_order(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

# 6. إلغاء الطلب
@orders_bp.route('/cancel/<string:order_id>', methods=['POST'])
def cancel_order_route(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    order.order_status = 'cancelled'
    try:
        db.session.commit()
        flash("تم إلغاء الطلب بنجاح.", "info")
    except Exception as e:
        db.session.rollback()
        flash("تعذر إلغاء الطلب.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

# 7. مسار البحث
@orders_bp.route('/search')
def search_orders():
    query = request.args.get('q', '')
    orders = ProcessedOrder.query.filter(ProcessedOrder.customer_name.contains(query)).all()
    # استخدام نفس القالب المحدث
    return render_template('admin/orders_dashboard.html', pagination=None, orders=orders)
