# coding: utf-8
# 📂 apps/suppliers_orders/routes.py

from flask import Blueprint, render_template, abort, session
from flask_login import login_required, current_user

# تعريف الـ Blueprint
suppliers_orders_bp = Blueprint('suppliers_orders', __name__, template_folder='templates')

@suppliers_orders_bp.route('/index', methods=['GET'])
@login_required
def index():
    """
    نافذة واحدة شاملة تعرض طلبات المورد (المعلقة والمكتملة).
    """
    # استيراد النماذج داخل الدالة لتجنب أي تعارض في الاستيراد (Circular Import)
    from apps.models.orders_db import Order
    
    # التحقق من نوع المستخدم وصلاحيته
    user_type = session.get('user_type')
    # تحديد معرف المورد بناءً على نوع المستخدم
    s_id = current_user.id if user_type == 'supplier' else getattr(current_user, 'supplier_id', None)
    
    if not s_id:
        abort(403)

    # جلب الطلبات الخاصة بالمورد مرتبة من الأحدث للأقدم
    orders = Order.query.filter_by(supplier_id=s_id).order_by(Order.id.desc()).all()
    
    # جلب الطلبات المنفصلة منطقياً للتبويبات (إن لزم الأمر)
    pending_orders = [o for o in orders if o.status == 'pending']
    completed_orders = [o for o in orders if o.status == 'completed']
    
    return render_template('suppliers/orders.html', 
                           orders=orders,
                           pending_orders=pending_orders,
                           completed_orders=completed_orders)

@suppliers_orders_bp.route('/details/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    from apps.models.orders_db import Order
    
    order = Order.query.get_or_404(order_id)
    
    # التحقق من صلاحية الوصول للطلب
    user_type = session.get('user_type')
    s_id = current_user.id if user_type == 'supplier' else getattr(current_user, 'supplier_id', None)
    
    if order.supplier_id != s_id:
        abort(403)
        
    return render_template('suppliers/order_details.html', order=order)
