# coding: utf-8
# 📂 apps/orders/routes.py - التحكم في مسارات الطلبات والمزامنة

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder, OrderItem
from apps.api.sync_engine import SyncEngine
from apps.models.suppliers import Supplier # تأكد من استيراد نموذج الموردين لديك
import logging

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')
logger = logging.getLogger(__name__)

# 1. لوحة تحكم الطلبات مع الترقيم (10 طلبات لكل صفحة)
@orders_bp.route('/dashboard')
def orders_dashboard():
    page = request.args.get('page', 1, type=int)
    # جلب الطلبات مرتبة من الأحدث للأقدم
    pagination = ProcessedOrder.query.order_by(ProcessedOrder.created_at_local.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    suppliers = Supplier.query.all()
    return render_template('orders/dashboard.html', pagination=pagination, suppliers=suppliers)

# 2. المزامنة الشاملة (تستدعي محرك المزامنة)
@orders_bp.route('/sync-all', methods=['POST'])
def sync_all():
    if SyncEngine.fetch_and_sync_order():
        flash("تمت مزامنة الطلبات بنجاح من قمرة كلاود.", "success")
    else:
        flash("فشل في المزامنة، يرجى مراجعة سجلات الخطأ.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

# 3. تحديث الحالات ديناميكياً (عبر AJAX)
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
        logger.error(f"خطأ في التحديث: {e}")
        db.session.rollback()
        
    return jsonify({'status': 'error'}), 400

# 4. تحديث المورد المحلي (عبر AJAX)
@orders_bp.route('/update-supplier/<string:order_id>', methods=['POST'])
def update_supplier(order_id):
    data = request.get_json()
    supplier_id = data.get('supplier_id')
    
    order = ProcessedOrder.query.get_or_404(order_id)
    order.supplier_id = supplier_id if supplier_id else None
    
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
    return render_template('orders/order_details.html', order=order)

# 6. إلغاء الطلب
@orders_bp.route('/cancel/<string:order_id>', methods=['POST'])
def cancel_order_route(order_id):
    order = ProcessedOrder.query.get_or_404(order_id)
    order.order_status = 'cancelled'
    db.session.commit()
    flash(f"تم إلغاء الطلب {order.order_id} بنجاح.", "info")
    return redirect(url_for('orders.orders_dashboard'))
