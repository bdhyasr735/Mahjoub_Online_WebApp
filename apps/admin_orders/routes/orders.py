# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
import threading
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify, Blueprint
from flask_login import login_required

from apps.extensions import db
from apps.services import services
from apps.models.orders_db import Order
from apps.models.supplier_db import Supplier
from apps.models.order_items_db import OrderItem

admin_orders_bp = Blueprint(
    'admin_orders_bp',
    __name__,
    template_folder='../templates',
    url_prefix='/admin/orders'
)

STATUS_TITLES_MAP = {
    'pending': 'قيد الانتظار',
    'processing': 'قيد التجهيز',
    'shipped': 'تم الشحن',
    'delivered': 'تم التسليم',
    'completed': 'مكتمل',
    'cancelled': 'ملغي',
    'refunded': 'مسترجع'
}


def _save_or_update_order_item(order_id, item_data):
    product_id = item_data.get('productId')
    if not product_id:
        return
    item = OrderItem.query.filter_by(order_id=order_id, product_qid=product_id).first()
    if not item:
        item = OrderItem(order_id=order_id, product_qid=product_id)

    item.quantity = item_data.get('quantity', 0)
    item.price = item_data.get('price', 0)
    product_data = item_data.get('productData', {})
    item.product_name = product_data.get('title', '')
    image_data = product_data.get('image', {})
    item.product_image = image_data.get('fileUrl', '')

    db.session.merge(item)
    db.session.commit()


def _save_or_update_order(order_data):
    order_id = order_data.get('_id')
    if not order_id:
        return

    order = Order.query.get(order_id)
    if not order:
        order = Order(id=order_id)

    # ✅ النظام يعتمد على الـ _id لتوليد رقم فريد وآمن
    try:
        order.order_number = int(order_id[:8], 16) % 1000000
    except:
        order.order_number = None

    # المرجع هو الـ _id
    order.order_reference = order_id
    
    account = order_data.get('account')
    if isinstance(account, dict):
        account_data = account.get('account', {})
        customer_name = account_data.get('fullname', 'زائر')
        order.customer_name = customer_name
        phone = account_data.get('phone')
        if phone:
            order.customer_phone = phone
    else:
        order.customer_name = 'زائر'
        
    shipping = order_data.get('shippingAddress', {})
    address = shipping.get('street') or shipping.get('description')
    if address:
        order.customer_address = address
        
    order.total_price = order_data.get('totalPrice', 0)
    status_obj = order_data.get('status', {})
    order.status_code = status_obj.get('code', 'pending')
    order.status_title = status_obj.get('title', 'قيد الانتظار')
    order.is_paid = order_data.get('isPaid', False)
    order.created_at = order_data.get('createdAt')
    updated_at = order_data.get('updatedAt')
    if updated_at:
        order.updated_at = updated_at
    
    items_list = order_data.get('items', [])
    order.items_count = len(items_list)

    db.session.merge(order)
    db.session.commit()

    for item_data in items_list:
        _save_or_update_order_item(order_id, item_data)

    order.items_count = len(items_list)
    db.session.commit()


def sync_all_orders_from_graphql(max_pages=None):
    page = 1
    limit = 50
    total_synced = 0

    print("\n🔍 [DEBUG] بدء مزامنة الطلبات من المصدر...")

    while True:
        try:
            print(f"⏳ جاري جلب الصفحة رقم {page}...")
            result = services.orders.get_all_orders(page=page, limit=limit)
            
            if not result:
                print("⛔ [DEBUG] الـ API رجع قيمة فارغة (None أو Empty)!")
                break

            orders = []
            has_next = False

            if isinstance(result, dict):
                orders = result.get('data', [])
                pagination = result.get('pagination', {}) or {}
                has_next = pagination.get('hasNextPage', False)
            elif isinstance(result, list):
                orders = result
                has_next = False

            print(f"📊 [DEBUG] عدد الطلبات الموجودة في هذه الصفحة: {len(orders)}")

            if not orders:
                print("⛔ [DEBUG] لا توجد طلبات في هذه الصفحة، ننهي التزامن.")
                break

            for order_data in orders:
                _save_or_update_order(order_data)
                total_synced += 1

            if not has_next:
                print("✅ [DEBUG] وصلنا لآخر صفحة، ننهي التزامن.")
                break

            if max_pages is not None and page >= max_pages:
                break

            page += 1

        except Exception as e:
            current_app.logger.error(f"خطأ في جلب الصفحة {page}: {e}")
            traceback.print_exc()
            break

    print(f"🏁 [DEBUG] انتهت المزامنة، إجمالي الطلبات التي تم جلبها وحفظها: {total_synced}")
    return total_synced


def _sync_orders_from_graphql(app=None):
    if app is None:
        app = current_app._get_current_object()
    with app.app_context():
        try:
            # ✅ التغيير الجذري: جلب الكل (max_pages=None)
            total = sync_all_orders_from_graphql(max_pages=None)
            current_app.logger.info(f"✅ تمت مزامنة {total} طلباً في الخلفية (تم جلب الكل)")
        except Exception as e:
            current_app.logger.error(f"❌ خطأ في مزامنة الطلبات الخلفية: {e}")


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
            thread = threading.Thread(target=_sync_orders_from_graphql, args=(app,), daemon=True)
            thread.start()

        query = Order.query

        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter(Order.status_code == status_filter)

        search = request.args.get('search')
        if search:
            query = query.filter(
                db.or_(
                    Order.order_number.ilike(f'%{search}%'),
                    Order._customer_name.ilike(f'%{search}%')
                )
            )

        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(Order.created_at >= date_from)

        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(Order.created_at <= date_to)

        query = query.order_by(Order.created_at.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        orders = paginated.items

        pagination_info = {
            'current_page': page,
            'total_pages': paginated.pages,
            'total_items': paginated.total,
            'has_prev': paginated.has_prev,
            'has_next': paginated.has_next,
            'prev_num': page - 1 if paginated.has_prev else None,
            'next_num': page + 1 if paginated.has_next else None,
        }

        suppliers = Supplier.query.all()

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info)
            })

        return render_template('admin/admin_orders.html',
                               orders=orders,
                               pagination=pagination_info,
                               suppliers=suppliers)

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض الطلبات: {traceback.format_exc()}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard_bp.dashboard'))


@admin_orders_bp.route('/sync', methods=['POST'], endpoint='sync_admin_orders')
@login_required
def sync_admin_orders():
    try:
        if session.get('user_type') != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح'}), 403

        total = sync_all_orders_from_graphql()
        return jsonify({'success': True, 'message': f'✅ تمت مزامنة {total} طلباً بنجاح.'})
    except Exception as e:
        current_app.logger.error(f"خطأ في المزامنة: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_orders_bp.route('/<string:order_id>/sync', methods=['POST'], endpoint='sync_single_order')
@login_required
def sync_single_order(order_id):
    try:
        order_data = services.orders.get_order_by_id(order_id)
        if order_data:
            _save_or_update_order(order_data)
            return jsonify({'success': True, 'message': 'تم تحديث الطلب'})
        return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404
    except Exception as e:
        current_app.logger.error(f"خطأ في مزامنة الطلب {order_id}: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    try:
        order = db.session.get(Order, order_id)
        if not order:
            order_data = services.orders.get_order_by_id(order_id)
            if order_data:
                _save_or_update_order(order_data)
                order = db.session.get(Order, order_id)

        if not order:
            flash('الطلب غير موجود', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

        items = OrderItem.query.filter_by(order_id=order_id).all()
        return render_template('admin/admin_order_detail.html', order=order, items_list=items)
    except Exception as e:
        current_app.logger.error(f"خطأ في عرض تفاصيل الطلب: {traceback.format_exc()}")
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('admin_orders_bp.list_admin_orders'))


@admin_orders_bp.route('/<string:order_id>/update-status', methods=['POST'], endpoint='update_order_status_inline')
@login_required
def update_order_status_inline(order_id):
    try:
        data = request.get_json() or {}
        new_status = data.get('status')
        if not new_status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.status_code = new_status
        order.status_title = STATUS_TITLES_MAP.get(new_status, 'غير معروف')
        db.session.commit()

        return jsonify({'success': True, 'message': 'تم تحديث الحالة'})
    except Exception as e:
        current_app.logger.error(f"خطأ في تحديث حالة الطلب: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)}), 500
