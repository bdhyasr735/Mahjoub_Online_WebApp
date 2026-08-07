# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
import threading
import time
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify, Blueprint
from flask_login import login_required

from apps.extensions import db
from apps.services import services
from apps.models.orders_db import Order
from apps.models.supplier_db import Supplier
from apps.models.order_items_db import OrderItem

# ✅ تعريف الـ Blueprint الرئيسي
admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='../templates',
    url_prefix='/admin/orders'
)

# 🏷️ خريطة المسميات العربية للحالات
STATUS_TITLES_MAP = {
    'pending': 'قيد الانتظار',
    'processing': 'قيد التجهيز',
    'shipped': 'تم الشحن',
    'delivered': 'تم التسليم',
    'completed': 'مكتمل',
    'cancelled': 'ملغي',
    'refunded': 'مسترجع'
}

def _sync_orders_in_background(app):
    """دالة مساعدة لإجراء المزامنة التلقائية للصفحة الأولى فقط في الخلفية."""
    with app.app_context():
        try:
            services.orders.get_all_orders(page=1, per_page=50)
        except Exception as sync_e:
            app.logger.warning(f"⚠️ [Auto Sync Orders Background] {sync_e}")

@admin_orders_bp.route('', methods=['GET'], endpoint='list_admin_orders')
@admin_orders_bp.route('/', methods=['GET'])
@login_required
def manage_admin_orders_view():
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))

        page = request.args.get('page', 1, type=int)
        per_page = 10
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not is_ajax:
            app = current_app._get_current_object()
            threading.Thread(target=_sync_orders_in_background, args=(app,), daemon=True).start()

        result = services.orders.get_local_orders(
            page=page,
            per_page=per_page,
            status=request.args.get('status'),
            search=request.args.get('search'),
            date_from=request.args.get('date_from'),
            date_to=request.args.get('date_to')
        )

        orders = result.get('data', [])
        pagination = result.get('pagination', {})
        pagination_info = {
            'current_page': page, 'total_pages': pagination.get('totalPages', 1),
            'total_items': pagination.get('totalItems', 0)
        }

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info)
            })

        return render_template('admin/admin_orders.html', orders=orders, pagination=pagination_info, suppliers=Supplier.query.all())
    except Exception as e:
        current_app.logger.error(f"خطأ في عرض الطلبات: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}) if request.headers.get('X-Requested-With') else "خطأ سيرفر"

@admin_orders_bp.route('/sync', methods=['POST'], endpoint='sync_admin_orders')
@login_required
def sync_admin_orders():
    """مزامنة شاملة للطلبات من المنصة"""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403
        
        # تنفيذ مزامنة الصفحة الأولى فوراً للسرعة
        services.orders.get_all_orders(page=1, per_page=20)
        return jsonify({'success': True, 'message': '✅ تمت مزامنة الطلبات بنجاح.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_orders_bp.route('/<string:order_id>/sync', methods=['POST'], endpoint='sync_single_order')
@login_required
def sync_single_order(order_id):
    """مزامنة طلب معين"""
    try:
        synced = services.orders.sync_single_order(order_id)
        if synced:
            return jsonify({'success': True, 'message': 'تم تحديث الطلب'})
        return jsonify({'success': False, 'message': 'فشل التحديث'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    order = db.session.get(Order, order_id)
    if not order and hasattr(services.orders, 'get_order_by_id'):
        services.orders.get_order_by_id(order_id)
        order = db.session.get(Order, order_id)
    
    if not order:
        flash('الطلب غير موجود', 'danger')
        return redirect(url_for('admin_orders_bp.list_admin_orders'))
        
    return render_template('admin/admin_order_detail.html', order=order, items_list=OrderItem.query.filter_by(order_id=order_id).all())

@admin_orders_bp.route('/<string:order_id>/update-status', methods=['POST'], endpoint='update_order_status_inline')
@login_required
def update_order_status_inline(order_id):
    data = request.get_json() or {}
    order = db.session.get(Order, order_id)
    if order:
        order.status_code = data.get('status')
        order.status_title = STATUS_TITLES_MAP.get(data.get('status'), 'غير معروف')
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404
