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

# ✅ تعريف الـ Blueprint الرئيسي مع تحديد مجلد القوالب
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

        # ✅ المزامنة التلقائية في الخلفية عند فتح أي صفحة (وليس فقط الأولى)
        if not is_ajax:
            app = current_app._get_current_object()
            threading.Thread(
                target=_sync_orders_in_background,
                args=(app, page, per_page),
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

        # ✅ جلب قائمة الموردين لتعبئة فلتر المورد
        suppliers_list = Supplier.query.all()

        if is_ajax:
            return jsonify({
                'success': True,
                'html': render_template('admin/partials/_orders_table.html', orders=orders, pagination=pagination_info),
                'pagination_html': render_template('admin/partials/_pagination.html', pagination=pagination_info),
                'total_items': pagination_info['total_items']
            })

        return render_template('admin/admin_orders.html', orders=orders, pagination=pagination_info, suppliers=suppliers_list)

    except Exception as e:
        current_app.logger.error(f"خطأ في جلب الطلبات للأدمن: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل الطلبات', 'danger')
        is_ajax = request.args.get('ajax', '0') == '1' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحميل الطلبات'}), 500
        return render_template('admin/admin_orders.html', orders=[], pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1}, suppliers=[])


@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    try:
        # 1. مسح أي معاملة قاعدة بيانات معلقة (ضمان نقاء الجلسة)
        db.session.rollback()
        
        # 2. البحث في قاعدة البيانات المحلية أولاً
        order = db.session.get(Order, order_id)
        
        # 3. إذا لم يكن موجوداً، قم بمزامنته فوراً ثم حاول جلبه مرة أخرى
        if not order:
            try:
                current_app.logger.info(f"🔄 محاولة مزامنة الطلب {order_id} عند فتح التفاصيل...")
                if hasattr(services.orders, 'sync_single_order'):
                    order = services.orders.sync_single_order(order_id)
                elif hasattr(services.orders, 'get_order_by_id'):
                    services.orders.get_order_by_id(order_id)
                    order = db.session.get(Order, order_id)
            except Exception as sync_e:
                current_app.logger.error(f"⚠️ خطأ أثناء مزامنة الطلب {order_id}: {sync_e}")
                db.session.rollback()

        # 4. التأكد من عدم وجود معاملة عالقة قبل الجلب النهائي
        db.session.rollback()
        order = db.session.get(Order, order_id)

        # 5. إذا ظل غير موجود، التوجيه مع التنبيه
        if not order:
            flash('❌ لم يتم العثور على الطلب في النظام، أو فشل حفظه محلياً. تأكد من صحة بيانات المزامنة.', 'danger')
            return redirect(url_for('admin_orders_bp.list_admin_orders'))

        # ✅ 6. جلب قائمة الموردين من قاعدة البيانات المحلية مباشرة
        suppliers = Supplier.query.all()  # جميع الموردين المحليين

        return render_template('admin/admin_order_detail.html', order=order, suppliers=suppliers)

    except Exception as e:
        current_app.logger.error(f"خطأ في عرض تفاصيل الطلب {order_id}: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل تفاصيل الطلب', 'danger')
        return redirect(url_for('admin_orders_bp.list_admin_orders'))


# (اختياري) يمكنك حذف هذه الدالة لأن الـ Decorators تغني عنها
def register_admin_orders_route(bp):
    bp.add_url_rule('', view_func=manage_admin_orders_view, methods=['GET'], endpoint='list_admin_orders')
    bp.add_url_rule('/<string:order_id>', view_func=view_admin_order, methods=['GET'], endpoint='view_admin_order')
    return bp


# ============================================================
# ✅ دالة المزامنة الشاملة (لزر "مزامنة الطلبات")
# ============================================================
@admin_orders_bp.route('/sync', methods=['POST'], endpoint='sync_admin_orders')
@login_required
def sync_admin_orders():
    """مزامنة جميع الطلبات من المنصة (جميع الصفحات) إلى قاعدة البيانات المحلية"""
    try:
        # التحقق من صلاحيات المستخدم
        user_type = session.get('user_type')
        if user_type != 'admin':
            return jsonify({'success': False, 'message': 'غير مصرح لك بهذه العملية'}), 403

        total_synced = 0
        current_page = 1
        per_page = 100  # جلب 100 طلب في كل مرة (لزيادة السرعة)

        # ✅ حلقة تكرار لجلب جميع الطلبات من جميع الصفحات
        while True:
            try:
                # جلب دفعة من الطلبات
                result = services.orders.get_all_orders(page=current_page, per_page=per_page)
                
                orders_data = result.get('data', [])
                pagination = result.get('pagination', {})

                # إذا لم يعد هناك بيانات، نكسر الحلقة
                if not orders_data:
                    break

                total_synced += len(orders_data)

                # التحقق مما إذا كان هناك صفحة تالية
                if not pagination.get('hasNextPage', False):
                    break

                # الانتقال للصفحة التالية
                current_page += 1
                
                # تأخير 1 ثانية لتجنب إرباك الخادم (Rate Limit)
                import time
                time.sleep(1)

            except Exception as inner_e:
                current_app.logger.error(f"⚠️ خطأ أثناء مزامنة الصفحة {current_page}: {inner_e}")
                break  # في حالة حدوث خطأ في صفحة، نوقف المحاولة

        return jsonify({
            'success': True,
            'message': f'✅ تمت المزامنة الكاملة! تم مزامنة {total_synced} طلب بنجاح.'
        })

    except Exception as e:
        current_app.logger.error(f"خطأ في مزامنة الطلبات: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء المزامنة: {str(e)}'
        }), 500
