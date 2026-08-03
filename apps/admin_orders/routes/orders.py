# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
import threading
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required

from apps.admin_orders.routes import admin_orders_bp
from apps.services import services
from apps.models.orders_db import Order
from apps.extensions import db

# 🏷️ خريطة المسميات العربية للحالات لتطابق السكيما ومظهر الواجهة
STATUS_TITLES_MAP = {
    'pending': 'قيد الانتظار',
    'processing': 'قيد التجهيز',
    'shipped': 'تم الشحن',
    'delivered': 'تم التسليم',
    'completed': 'مكتمل',
    'cancelled': 'ملغي',
    'refunded': 'مسترجع'
}


def _sync_orders_in_background(app, page=1, per_page=15):
    """دالة مساعدة لإجراء المزامنة في الخلفية دون تعطيل طلبات المتصفح."""
    with app.app_context():
        try:
            services.orders.get_all_orders(page=page, per_page=per_page)
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
        per_page = request.args.get('limit', 10, type=int)
        per_page = max(1, min(per_page, 50))
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        status_filter = request.args.get('status', '').strip()
        search_term = request.args.get('search', '').strip().lower()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        # 🚀 تشغيل المزامنة في الخلفية عند فتح الصفحة الأولى وبدون تصفية
        if not is_ajax and page == 1 and not (search_term or status_filter or date_from or date_to):
            app = current_app._get_current_object()
            threading.Thread(
                target=_sync_orders_in_background,
                args=(app, 1, 15),
                daemon=True
            ).start()

        # ⚡ جلب فوري ومباشر للطلبات من قاعدة البيانات المحلية
        result = services.orders.get_local_orders(
            page=page,
            per_page=per_page,
            status=status_filter if status_filter else None,
            search=search_term if search_term else None,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None
        )

        orders = result.get('data', [])
        pagination = result.get('pagination', {})

        pagination_info = {
            'current_page': page,
            'total_pages': pagination.get('totalPages', 1),
            'has_prev': page > 1,
            'has_next': page < pagination.get('totalPages', 1),
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if page < pagination.get('totalPages', 1) else None,
            'per_page': per_page,
            'total_items': pagination.get('totalItems', 0)
        }

        for order in orders:
            if 'status_text' not in order:
                order['status_text'] = order.get('status_title', 'غير معروف')

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders, pagination=pagination_info),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info),
                'total_items': pagination_info['total_items']
            })

        return render_template('admin/admin_orders.html', orders=orders, pagination=pagination_info)

    except Exception as e:
        current_app.logger.error(f"خطأ في جلب الطلبات للأدمن: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل الطلبات', 'danger')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحميل الطلبات'}), 500
        return render_template('admin/admin_orders.html', orders=[], pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1})


@admin_orders_bp.route('/sync', methods=['POST'])
@login_required
def sync_admin_orders():
    try:
        app = current_app._get_current_object()
        threading.Thread(
            target=_sync_orders_in_background,
            args=(app, 1, 50),
            daemon=True
        ).start()

        return jsonify({'success': True, 'message': '⚡ بدأت عملية المزامنة في الخلفية بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_orders_bp.route('/<string:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    try:
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form

        new_status = data.get('status') or data.get('status_code')
        if not new_status:
            return jsonify({'success': False, 'message': 'الحالة مطلوبة'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        # 1️⃣ تحديث قاعدة البيانات المحلية
        order.status_code = new_status
        if new_status in STATUS_TITLES_MAP:
            order.status_title = STATUS_TITLES_MAP[new_status]
        order.updated_at = datetime.utcnow()
        
        db.session.commit()

        # 2️⃣ إرسال تحديث الحالة إلى الخدمة الخارجية
        if hasattr(services.orders, 'update_order_status'):
            try:
                services.orders.update_order_status(order_id, new_status)
            except Exception as service_e:
                current_app.logger.warning(f"⚠️ فشل تحديث الخدمة الخارجية: {service_e}")

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': 'تم تحديث حالة الطلب بنجاح',
                'status_code': order.status_code,
                'status_title': order.status_title
            })

        flash('✅ تم تحديث حالة الطلب بنجاح', 'success')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تحديث حالة الطلب {order_id}: {traceback.format_exc()}")
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
            
        flash('❌ حدث خطأ أثناء تحديث الحالة', 'danger')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))


@admin_orders_bp.route('/<string:order_id>/financial-status', methods=['POST'])
@login_required
def update_financial_status(order_id):
    """تحديث الحالة المالية للطلب (مدفوع / غير مدفوع / مسترجع)."""
    try:
        data = request.get_json() if request.is_json else request.form
        new_status = data.get('financial_status') or data.get('status')
        if not new_status:
            return jsonify({'success': False, 'message': 'الحالة المالية مطلوبة'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.financial_status = new_status
        if hasattr(order, 'is_paid'):
            order.is_paid = (new_status in ['paid', 'completed'])
        order.updated_at = datetime.utcnow()
        db.session.commit()

        if hasattr(services.orders, 'update_financial_status'):
            try:
                services.orders.update_financial_status(order_id, new_status)
            except Exception as service_e:
                current_app.logger.warning(f"⚠️ فشل تحديث الحالة المالية في الخدمة الخارجية: {service_e}")

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': 'تم تحديث حالة الدفع بنجاح',
                'financial_status': order.financial_status
            })

        flash('✅ تم تحديث حالة الدفع بنجاح', 'success')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تحديث الحالة المالية للطلب {order_id}: {traceback.format_exc()}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash('❌ حدث خطأ أثناء تحديث حالة الدفع', 'danger')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))


@admin_orders_bp.route('/<string:order_id>/fulfillment-status', methods=['POST'])
@login_required
def update_fulfillment_status(order_id):
    """تحديث حالة الشحن والتسليم."""
    try:
        data = request.get_json() if request.is_json else request.form
        new_status = data.get('fulfillment_status') or data.get('status')
        if not new_status:
            return jsonify({'success': False, 'message': 'حالة الشحن مطلوبة'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'الطلب غير موجود'}), 404

        order.fulfillment_status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()

        if hasattr(services.orders, 'update_fulfillment_status'):
            try:
                services.orders.update_fulfillment_status(order_id, new_status)
            except Exception as service_e:
                current_app.logger.warning(f"⚠️ فشل تحديث حالة الشحن الخارجية: {service_e}")

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': 'تم تحديث حالة الشحن بنجاح',
                'fulfillment_status': order.fulfillment_status
            })

        flash('✅ تم تحديث حالة الشحن بنجاح', 'success')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في تحديث حالة الشحن للطلب {order_id}: {traceback.format_exc()}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        flash('❌ حدث خطأ أثناء تحديث حالة الشحن', 'danger')
        return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order_id))


@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    try:
        # 1. البحث في قاعدة البيانات المحلية أولاً
        order = Order.query.get(order_id)
        
        # 2. إذا لم يكن موجوداً محلياً، جلب الطلب فوراً من API الخارجية وتخزينه
        if not order:
            try:
                if hasattr(services.orders, 'get_order_by_id'):
                    order = services.orders.get_order_by_id(order_id)
                elif hasattr(services.orders, 'sync_single_order'):
                    order = services.orders.sync_single_order(order_id)
            except Exception as sync_single_e:
                current_app.logger.warning(f"⚠️ تعذر جلب الطلب {order_id} من الخدمة الخارجية: {sync_single_e}")

        # 3. التأكد من إعادة المحاولة محلياً بعد الجلب
        if not order:
            order = Order.query.get(order_id)

        # 4. إذا ظل غير موجود، يتم التوجيه مع التنبيه
        if not order:
            flash('❌ لم يتم العثور على الطلب في النظام', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

        # 5. جلب قائمة الموردين لتعبئة القائمة المنسدلة في صفحة تفاصيل الطلب
        suppliers = []
        try:
            if hasattr(services, 'suppliers') and hasattr(services.suppliers, 'get_all_suppliers'):
                suppliers = services.suppliers.get_all_suppliers()
        except Exception:
            pass

        return render_template('admin/admin_order_detail.html', order=order, suppliers=suppliers)

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض تفاصيل الطلب {order_id}: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل تفاصيل الطلب', 'danger')
        return redirect(url_for('admin_orders_bp.list_admin_orders'))


def register_admin_orders_route(bp):
    bp.add_url_rule('', view_func=manage_admin_orders_view, methods=['GET'], endpoint='list_admin_orders')
    bp.add_url_rule('/sync', view_func=sync_admin_orders, methods=['POST'])
    bp.add_url_rule('/<string:order_id>/status', view_func=update_order_status, methods=['POST'])
    bp.add_url_rule('/<string:order_id>/financial-status', view_func=update_financial_status, methods=['POST'])
    bp.add_url_rule('/<string:order_id>/fulfillment-status', view_func=update_fulfillment_status, methods=['POST'])
    bp.add_url_rule('/<string:order_id>', view_func=view_admin_order, methods=['GET'], endpoint='view_admin_order')
    return bp
