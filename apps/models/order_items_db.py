# coding: utf-8
# 📂 المسار المقترح لتحديث لوحة تحكم المورد (أو جزء مسارات الطلبات فيها)

from flask import Blueprint, render_template, request, jsonify, session, abort
from apps.services.order_service import OrderService
from apps.services.graphql_client import GraphQLClient
from apps.models.orders_db import Order
from apps.extensions import db

supplier_orders_bp = Blueprint('supplier_orders', __name__, url_prefix='/supplier/orders')

# تهيئة الخدمات
graphql_client = GraphQLClient() # تأكد من تمرير الإعدادات المناسبة هنا حسب مشروعك
order_service = OrderService(graphql_client)

@supplier_orders_bp.route('/', methods=['GET'])
def list_supplier_orders():
    """عرض قائمة الطلبات الخاصة بالمورد المحلي الحالي"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        abort(403) # أو إعادة التوجيه لصفحة تسجيل الدخول

    page = request.args.get('page', 1, type=int)
    per_page = 15
    status = request.args.get('status', type=str)
    search = request.args.get('search', type=str)
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)

    # جلب الطلبات عبر خدمة الطلبات مع فلترة المورد المحلي تلقائياً
    result = order_service.get_local_orders(
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
        orders=result['data'],
        pagination=result['pagination'],
        current_status=status,
        search_query=search
    )


@supplier_orders_bp.route('/<string:order_id>', methods=['GET'])
def view_supplier_order_detail(order_id):
    """عرض تفاصيل طلب معين مع التركيز على بنود وعناصر المورد الحالي"""
    supplier_id = session.get('supplier_id')
    if not supplier_id:
        abort(403)

    # جلب الطلب محلياً أو مزامنته فوراً
    order = order_service.get_order_by_id(order_id)
    if not order:
        abort(404)

    # تصفية بنود الطلب لتظهر للمورد العناصر التي تخصه فقط (إن طُلب ذلك في العرض)
    # أو تمرير الطلب كاملاً مع تمييز عناصره
    order_dict = order.to_dict()
    
    # تصفية العناصر الخاصة بهذا المورد إذا أراد المورد رؤية بنوده فقط
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
