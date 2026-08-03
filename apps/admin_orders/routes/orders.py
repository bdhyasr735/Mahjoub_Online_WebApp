# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required
from apps.admin_orders.routes import admin_orders_bp
from apps.services import services
from apps.models.supplier_db import Supplier
from apps.models.orders_db import Order
from apps.extensions import db
from datetime import datetime


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
        financial_status_filter = request.args.get('financial_status', '').strip()
        fulfillment_status_filter = request.args.get('fulfillment_status', '').strip()
        search_term = request.args.get('search', '').strip().lower()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        supplier_filter = request.args.get('supplier_id', type=int)

        if not is_ajax:
            try:
                services.orders.get_all_orders(page=page, per_page=50)
            except Exception as sync_e:
                print(f"⚠️ [Auto Sync Orders] {sync_e}")

        # ✅ جلب الطلبات مع الفلاتر الجديدة
        result = services.orders.get_local_orders(
            page=page,
            per_page=per_page,
            supplier_id=supplier_filter,
            status=status_filter if status_filter else None,
            search=search_term if search_term else None,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None
        )

        orders = result.get('data', [])
        pagination = result.get('pagination', {})
        suppliers = Supplier.query.filter_by(status='active').all()

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

        # تحويل الحالة للعربية والترقيم اليدوي
        for idx, order in enumerate(orders):
            # تعيين الترقيم التسلسلي
            order['row_num'] = idx + 1 + (page - 1) * per_page
            # تعيين النصوص العربية للحالات
            status_map = {
                'pending': 'قيد الانتظار',
                'confirmed': 'مؤكد',
                'processing': 'قيد المعالجة',
                'shipped': 'تم الشحن',
                'delivered': 'تم التسليم',
                'cancelled': 'ملغي',
                'refunded': 'مسترد',
                'returned': 'مرتجع'
            }
            order['status_label'] = status_map.get(order.get('status', ''), order.get('status', 'غير معروف'))

            # تعيين الحالة المالية
            financial_map = {'paid': 'مدفوع', 'unpaid': 'غير مدفوع', 'refunded': 'مسترد'}
            order['financial_status_label'] = financial_map.get(order.get('financial_status', ''), 'غير معروف')

            # تعيين حالة الشحن
            fulfillment_map = {'fulfilled': 'مكتمل', 'unfulfilled': 'غير مكتمل', 'partial': 'جزئي'}
            order['fulfillment_status_label'] = fulfillment_map.get(order.get('fulfillment_status', ''), 'غير معروف')

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders, pagination=pagination_info, suppliers=suppliers),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info),
                'total_items': pagination_info['total_items']
            })

        return render_template('admin/admin_orders.html', orders=orders, pagination=pagination_info, suppliers=suppliers)

    except Exception as e:
        current_app.logger.error(f"خطأ في جلب الطلبات للأدمن: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل الطلبات', 'danger')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحميل الطلبات'}), 500
        return render_template('admin/admin_orders.html', orders=[], pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1}, suppliers=[])


# ... باقي المسارات (update_status, update_supplier, view, register) كما هي ...
