# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
import threading
import time
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify, Blueprint
from flask_login import login_required
from sqlalchemy import or_

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

# ============================================================
# دوال مساعدة للمزامنة والتخزين المحلي
# ============================================================

def _save_order_to_local(order_data):
    """حفظ أو تحديث طلب في قاعدة البيانات المحلية من بيانات GraphQL."""
    order_id = order_data.get('_id')
    if not order_id:
        return

    order = Order.query.get(order_id)
    if not order:
        order = Order(_id=order_id)

    # تعيين الحقول الأساسية
    order.order_number = order_data.get('orderNumber') or order_id[:8]
    order.customer_name = order_data.get('account', {}).get('account', {}).get('fullname', 'زائر')
    order.total_price = order_data.get('totalPrice', 0)
    order.status_code = order_data.get('status', {}).get('code', 'pending')
    order.status_title = order_data.get('status', {}).get('title', 'قيد الانتظار')
    order.is_paid = order_data.get('isPaid', False)
    order.created_at = order_data.get('createdAt')
    # يمكن إضافة حقول أخرى حسب الحاجة (مثل totalPriceWithTax, currency, إلخ)

    db.session.merge(order)
    db.session.commit()

    # حفظ عناصر الطلب
    for item_data in order_data.get('items', []):
        product_id = item_data.get('productId')
        if not product_id:
            continue
        item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()
        if not item:
            item = OrderItem(order_id=order_id, product_id=product_id)
        item.quantity = item_data.get('quantity', 0)
        item.price = item_data.get('price', 0)
        item.product_title = item_data.get('productData', {}).get('title', '')
        # يمكن إضافة حقول أخرى كالصورة أو الخيارات
        db.session.merge(item)
    db.session.commit()

def _sync_orders_from_graphql(max_pages=5):
    """مزامنة عدد من الصفحات من GraphQL إلى المحلية."""
    for page in range(1, max_pages + 1):
        result = services.orders.get_all_orders(page=page, limit=50)  # استخدم الدالة الموجودة
        orders = result.get('data', [])
        if not orders:
            break
        for order_data in orders:
            _save_order_to_local(order_data)
    return True

def _sync_single_order_from_graphql(order_id):
    """مزامنة طلب واحد من GraphQL إلى المحلية."""
    order_data = services.orders.get_order_by_id(order_id)  # الدالة الموجودة
    if order_data:
        _save_order_to_local(order_data)
        return True
    return False

# ============================================================
# المسارات (Routes)
# ============================================================

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

        # مزامنة تلقائية في الخلفية (اختياري) لأول صفحة فقط
        if not is_ajax:
            app = current_app._get_current_object()
            threading.Thread(target=_sync_orders_from_graphql, args=(app, 1), daemon=True).start()

        # بناء الاستعلام المحلي مع الفلاتر
        query = Order.query
        status = request.args.get('status')
        search = request.args.get('search')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        if status:
            query = query.filter(Order.status_code == status)
        if search:
            query = query.filter(
                or_(
                    Order.order_number.ilike(f'%{search}%'),
                    Order.customer_name.ilike(f'%{search}%')
                )
            )
        if date_from:
            query = query.filter(Order.created_at >= date_from)
        if date_to:
            query = query.filter(Order.created_at <= date_to)

        # تنفيذ الترقيم
        paginated = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        orders = paginated.items
        pagination_info = {
            'current_page': paginated.page,
            'total_pages': paginated.pages,
            'total_items': paginated.total,
            'has_prev': paginated.has_prev,
            'has_next': paginated.has_next,
            'prev_num': paginated.prev_num,
            'next_num': paginated.next_num
        }

        # إذا كان طلب AJAX، نعيد JSON مع الأجزاء
        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info)
            })

        # عرض الصفحة كاملة
        suppliers = Supplier.query.all()
        return render_template('admin/admin_orders.html', orders=orders, pagination=pagination_info, suppliers=suppliers)

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض الطلبات: {traceback.format_exc()}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))

@admin_orders_bp.route('/sync', methods=['POST'], endpoint='sync_admin_orders')
@login_required
def sync_admin_orders():
    """مزامنة شاملة للطلبات من المنصة (عدد محدد من الصفحات)."""
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        # مزامنة أول 5 صفحات (يمكن تعديل العدد)
        _sync_orders_from_graphql(max_pages=5)
        return jsonify({'success': True, 'message': '✅ تمت مزامنة الطلبات بنجاح.'})
    except Exception as e:
        current_app.logger.error(f"خطأ في المزامنة: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_orders_bp.route('/<string:order_id>/sync', methods=['POST'], endpoint='sync_single_order')
@login_required
def sync_single_order(order_id):
    """مزامنة طلب معين."""
    try:
        if _sync_single_order_from_graphql(order_id):
            return jsonify({'success': True, 'message': 'تم تحديث الطلب'})
        return jsonify({'success': False, 'message': 'فشل التحديث'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    """عرض تفاصيل طلب معين، مع مزامنة تلقائية إذا لم يكن موجوداً محلياً."""
    order = Order.query.get(order_id)
    if not order:
        # محاولة مزامنة الطلب من GraphQL
        if _sync_single_order_from_graphql(order_id):
            order = Order.query.get(order_id)
        if not order:
            flash('الطلب غير موجود', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

    items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('admin/admin_order_detail.html', order=order, items_list=items)

@admin_orders_bp.route('/<string:order_id>/update-status', methods=['POST'], endpoint='update_order_status_inline')
@login_required
def update_order_status_inline(order_id):
    """تحديث حالة الطلب محلياً (مع إمكانية إضافة تحديث عبر GraphQL لاحقاً)."""
    data = request.get_json() or {}
    new_status = data.get('status')
    order = Order.query.get(order_id)
    if order and new_status in STATUS_TITLES_MAP:
        order.status_code = new_status
        order.status_title = STATUS_TITLES_MAP[new_status]
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'الطلب غير موجود أو حالة غير صالحة'}), 404
