# coding: utf-8
# 📂 apps/supplier_orders/routes.py

from flask import Blueprint, render_template, request, jsonify, session, abort
from apps.services import services
from apps.models.orders_db import Order
from apps.extensions import db

supplier_orders_bp = Blueprint('supplier_orders', __name__, url_prefix='/supplier/orders')

@supplier_orders_bp.route('/', methods=['GET'])
def list_supplier_orders():
    """عرض قائمة الطلبات الخاصة بالمورد المحلي الحالي"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 15
    status = request.args.get('status', type=str)
    search = request.args.get('search', type=str)
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)

    # جلب الطلبات عبر خدمة الطلبات المركزية مع فلترة المورد المحلي تلقائياً
    result = services.orders.get_local_orders(
        page=page,
        per_page=per_page,
        supplier_id=supplier_id,
        status=status,
        search=search,
        date_from=date_from,
        date_to=date_to
    )

    return render_template(
        'supplier/orders_dashboard.html',
        orders=result.get('data', []),
        pagination=result.get('pagination', {}),
        current_status=status,
        search_query=search
    )


@supplier_orders_bp.route('/<string:order_id>', methods=['GET'])
def view_supplier_order_detail(order_id):
    """عرض تفاصيل طلب معين مع التركيز على بنود وعناصر المورد الحالي"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        abort(403)

    # جلب الطلب محلياً أو مزامنته فوراً عبر الخدمة المركزية
    order = Order.query.get(order_id)
    if not order:
        try:
            if hasattr(services.orders, 'get_order_by_id'):
                order = services.orders.get_order_by_id(order_id)
        except Exception:
            pass

    if not order:
        abort(404)

    # تحويل البيانات إلى قاموس بأمان
    order_dict = order.to_dict() if hasattr(order, 'to_dict') else {
        'id': getattr(order, 'id', order_id),
        'status': getattr(order, 'status', ''),
        'items': getattr(order, 'items', [])
    }
    
    # تصفية عناصر الطلب لتقتصر حصراً على البنود التي تخص المورد الحالي
    filtered_items = [
        item for item in order_dict.get('items', []) 
        if item.get('supplier_id') == supplier_id
    ]

    return render_template(
        'supplier/order_detail.html',
        order=order_dict,
        supplier_items=filtered_items,
        current_supplier_id=supplier_id
    )
