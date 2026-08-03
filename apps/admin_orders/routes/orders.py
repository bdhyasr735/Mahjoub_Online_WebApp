# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required
from apps.admin_orders.routes import admin_orders_bp
from apps.services import services


@admin_orders_bp.route('/orders', methods=['GET'], endpoint='list_admin_orders')
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

        # ✅ مزامنة تلقائية للصفحة الحالية عند كل زيارة
        if not is_ajax:
            try:
                services.orders.get_all_orders(page=page, per_page=50)
            except Exception as sync_e:
                print(f"⚠️ [Auto Sync Orders] حدث خطأ أثناء المزامنة التلقائية: {sync_e}")

        # ✅ جلب الطلبات من قاعدة البيانات المحلية
        result = services.orders.get_local_orders(
            page=page,
            per_page=per_page,
            supplier_id=None,  # الأدمن يرى جميع الطلبات
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
                order['status_text'] = order.get('status', 'غير معروف').title()

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


# ============================================================================================
# ✅ مسار عرض تفاصيل الطلب (لحل مشكلة BuildError)
# ============================================================================================
@admin_orders_bp.route('/orders/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))

        # هنا يمكنك جلب الطلب من قاعدة البيانات المحلية أو عبر الخدمة
        # مثال مؤقت:
        from apps.models.orders_db import Order
        order = Order.query.get(order_id)
        
        if not order:
            flash('❌ لم يتم العثور على الطلب', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

        return render_template('admin/admin_order_detail.html', order=order)

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض تفاصيل الطلب: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل تفاصيل الطلب', 'danger')
        return redirect(url_for('admin_orders_bp.list_admin_orders'))


# ============================================================================================
# ✅ دالة تسجيل المسارات
# ============================================================================================
def register_admin_orders_route(bp):
    bp.add_url_rule('/orders', view_func=manage_admin_orders_view, methods=['GET'], endpoint='list_admin_orders')
    bp.add_url_rule('/orders/<string:order_id>', view_func=view_admin_order, methods=['GET'], endpoint='view_admin_order')
    return bp
