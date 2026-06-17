# coding: utf-8
# 📂 apps/orders/routes.py - إدارة الطلبات (النسخة المتوافقة مع التحديثات)

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from apps.models.orders_db import ProcessedOrder, db
from apps.api.sync_engine import SyncEngine
import logging

orders_blueprint = Blueprint('orders', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

@orders_blueprint.route('/dashboard', methods=['GET'])
@login_required
def orders_dashboard():
    """عرض قائمة الطلبات مع الترقيم"""
    page = request.args.get('page', 1, type=int)
    # جلب الطلبات مرتبة من الأحدث
    pagination = ProcessedOrder.query.order_by(ProcessedOrder.created_at_api.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin/orders_dashboard.html', pagination=pagination)

@orders_blueprint.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """مزامنة شاملة من قمرة"""
    try:
        success = SyncEngine.fetch_and_sync_order()
        if success:
            flash("✅ تمت مزامنة الطلبات بنجاح من قمرة.", "success")
        else:
            flash("⚠️ فشلت المزامنة. يرجى التحقق من السجلات.", "danger")
    except Exception as e:
        logger.error(f"❌ خطأ في المزامنة: {e}")
        flash(f"حدث خطأ تقني: {str(e)}", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order_route(order_id):
    result = SyncEngine.cancel_order(order_id)
    # فحص النتيجة بناءً على هيكلية GraphQL
    if result and 'errors' not in result.get('data', {}):
        flash(f"تم إلغاء الطلب {order_id}.", "info")
    else:
        flash("فشل إلغاء الطلب في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/fulfill/<order_id>', methods=['POST'])
@login_required
def fulfill_order_route(order_id):
    result = SyncEngine.mark_as_fulfilled(order_id)
    if result and 'errors' not in result.get('data', {}):
        flash(f"تم تحديث الطلب {order_id} إلى 'مشحون'.", "success")
    else:
        flash("فشل تحديث الشحن.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/process/<order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    order = ProcessedOrder.query.get(order_id)
    if not order:
        flash("الطلب غير موجود محلياً.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
    
    try:
        order.status = 'settled'
        db.session.commit()
        flash(f"تمت التسوية المالية للطلب {order_id}.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ في التسوية: {e}")
        flash("فشل التسوية المالية.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/update-status/<order_id>', methods=['POST'])
@login_required
def update_status_route(order_id):
    new_status = request.form.get('status')
    if not new_status:
        flash("حالة غير صالحة.", "warning")
        return redirect(url_for('orders.orders_dashboard'))
        
    result = SyncEngine.update_order_status(order_id, new_status)
    if result and 'errors' not in result.get('data', {}):
        flash(f"تم تحديث حالة الطلب {order_id}.", "success")
    else:
        flash("فشل التحديث في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))
