# coding: utf-8
# 📂 apps/orders/routes.py - لوحة تحكم الطلبات والعمليات (النسخة النهائية المحدثة)

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
    """عرض لوحة التحكم مع كافة بيانات الطلبات"""
    # جلب كافة الطلبات مرتبة من الأحدث للأقدم
    orders = ProcessedOrder.query.order_by(ProcessedOrder.created_at_api.desc()).all()
    return render_template('admin/orders_dashboard.html', orders=orders)

@orders_blueprint.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """مزامنة شاملة لجميع الطلبات وتحديث كافة حقولها من قمرة"""
    # استدعاء المحرك
    success = SyncEngine.fetch_and_sync_order()
    if success:
        flash("تمت مزامنة الطلبات وتحديث البيانات بنجاح.", "success")
    else:
        flash("فشلت المزامنة، يرجى التحقق من سجلات النظام (Logs) للتأكد من اتصال API.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/cancel/<order_id>', methods=['POST'])
@login_required
def cancel_order_route(order_id):
    """إلغاء الطلب في قمرة ومحلياً"""
    result = SyncEngine.cancel_order(order_id)
    if result:
        flash(f"تم تنفيذ طلب الإلغاء للطلب {order_id}.", "info")
    else:
        flash(f"تعذر إلغاء الطلب {order_id} من منصة قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/fulfill/<order_id>', methods=['POST'])
@login_required
def fulfill_order_route(order_id):
    """تحديث حالة الطلب كـ مشحون في قمرة"""
    result = SyncEngine.mark_as_fulfilled(order_id)
    if result:
        flash(f"تم تحديث الطلب {order_id} ليكون مشحوناً.", "success")
    else:
        flash(f"خطأ: لم يتم تحديث حالة الشحن في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/process/<order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    """تسوية مالية محلية للطلب"""
    order = ProcessedOrder.query.get(order_id)
    if not order:
        flash("الطلب غير موجود في قاعدة البيانات.", "danger")
        return redirect(url_for('orders.orders_dashboard'))
    
    try:
        # تحديث الحالة محلياً
        order.status = 'settled'
        db.session.commit()
        flash(f"تمت التسوية المالية للطلب {order_id} بنجاح.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ [Financial Error] Order ID {order_id}: {e}")
        flash("حدث خطأ أثناء عملية التسوية المالية.", "danger")
        
    return redirect(url_for('orders.orders_dashboard'))

@orders_blueprint.route('/update-status/<order_id>', methods=['POST'])
@login_required
def update_status_route(order_id):
    """تحديث حالة الطلب يدوياً"""
    new_status = request.form.get('status')
    if not new_status:
        flash("يرجى اختيار حالة صالحة.", "warning")
        return redirect(url_for('orders.orders_dashboard'))
        
    result = SyncEngine.update_order_status(order_id, new_status)
    if result:
        flash(f"تم تغيير حالة الطلب {order_id} إلى {new_status}.", "success")
    else:
        flash("فشل تحديث الحالة في قمرة.", "danger")
    return redirect(url_for('orders.orders_dashboard'))
