# coding: utf-8
# 📂 apps/suppliers_orders/routes/orders.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from apps.suppliers_orders.routes import suppliers_orders_bp
from apps.services import services
from apps.extensions import db
from datetime import datetime


@suppliers_orders_bp.route('/orders', methods=['GET'], endpoint='list_supplier_orders')
@login_required
def manage_supplier_orders_view():
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        user_type = getattr(current_user, 'user_type', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        per_page = max(1, min(per_page, 50))
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        status_filter = request.args.get('status', '').strip()
        search_term = request.args.get('search', '').strip().lower()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        # جلب الطلبات من الخدمة مع الفلاتر
        result = services.orders.get_all_orders(
            page=page, 
            per_page=per_page, 
            supplier_id=supplier_id,
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
            order['status_text'] = order.get('status', '').upper()

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('suppliers/partials/_orders_table.html', orders=orders, pagination=pagination_info),
                'pagination_html': render_template('suppliers/partials/_pagination.html', pagination=pagination_info),
                'total_items': pagination_info['total_items']
            })

        return render_template('suppliers/orders_dashboard.html', orders=orders, pagination=pagination_info)

    except Exception as e:
        current_app.logger.error(f"خطأ في جلب الطلبات: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل الطلبات', 'danger')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحميل الطلبات'}), 500
        
        return render_template('suppliers/orders_dashboard.html', orders=[], pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1})


# ============================================================================================
# ✅ الحل الجذري: إضافة دالة تسجيل المسارات لتتوافق مع __init__.py
# ============================================================================================
def register_orders_route(bp):
    # إضافة مسار عرض الطلبات (قائمة المورد) باستخدام add_url_rule
    bp.add_url_rule('/orders', view_func=manage_supplier_orders_view, methods=['GET'], endpoint='list_supplier_orders')
    return bp
