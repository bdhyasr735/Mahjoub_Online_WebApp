# coding: utf-8
# 📂 apps/suppliers_orders/routes.py

from flask import Blueprint, render_template, abort, session, request
from flask_login import login_required, current_user
from apps.models.orders_db import Order
from apps.orders.services import OrderService

# تعريف الـ Blueprint مع تحديد مجلد القوالب المحلي
suppliers_orders_bp = Blueprint('suppliers_orders', __name__, template_folder='templates')

@suppliers_orders_bp.route('/index', methods=['GET'])
@login_required
def index():
    user_type = session.get('user_type')
    s_id = current_user.id if user_type == 'supplier' else getattr(current_user, 'supplier_id', None)
    
    if s_id is None:
        abort(403)

    page = request.args.get('page', 1, type=int)
    
    # تحويل s_id إلى int بأمان
    try:
        supplier_id = int(s_id)
    except:
        abort(400)

    pagination = Order.query.filter_by(supplier_id=supplier_id).order_by(Order.id.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    context = {
        'orders': pagination.items, 
        'pagination': pagination
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # تأكد أن اسم الملف داخل مجلد templates الخاص بالموديول
        return render_template('suppliers_orders/_table.html', **context)
        
    return render_template('suppliers_orders/dashboard.html', **context)

@suppliers_orders_bp.route('/details/<string:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    order, financial = OrderService.get_order_details(order_id)
    
    if not order:
        abort(404)
    
    user_type = session.get('user_type')
    s_id = current_user.id if user_type == 'supplier' else getattr(current_user, 'supplier_id', None)
    
    if str(order.supplier_id) != str(s_id):
        abort(403)
        
    return render_template('suppliers_orders/details.html', order=order, financial=financial)
