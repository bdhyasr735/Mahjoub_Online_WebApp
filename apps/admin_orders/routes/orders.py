# coding: utf-8
# 📂 apps/admin_orders/routes/orders.py

import traceback
import threading
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify, Blueprint  # ← أضف Blueprint هنا
from flask_login import login_required

# ❌ احذف هذا السطر نهائياً: from apps.admin_orders import admin_orders_bp
from apps.extensions import db
from apps.services import services
from apps.models.orders_db import Order

# ✅ عرّف الـ Blueprint هنا (هذا هو الحل السحري)
admin_orders_bp = Blueprint('admin_orders_bp', __name__, url_prefix='/admin/orders')


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
    # ... باقي الكود كما هو (لم يتغير) ...


@admin_orders_bp.route('/<string:order_id>', methods=['GET'], endpoint='view_admin_order')
@login_required
def view_admin_order(order_id):
    # ... باقي الكود كما هو (لم يتغير) ...


# يمكنك الاحتفاظ بهذه الدالة أو حذفها، لكنها لن تؤثر لأن الـ Decorators تغني عنها.
def register_admin_orders_route(bp):
    bp.add_url_rule('', view_func=manage_admin_orders_view, methods=['GET'], endpoint='list_admin_orders')
    bp.add_url_rule('/<string:order_id>', view_func=view_admin_order, methods=['GET'], endpoint='view_admin_order')
    return bp
