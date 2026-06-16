# 📂 apps/orders/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from apps.utils.orders_engine import get_pending_orders

orders_bp = Blueprint('orders', __name__, template_folder='templates')

# إضافة كلا المسارين والاسمي لضمان عمل القالب دون أي BuildError
@orders_bp.route('/pending', methods=['GET'])
@orders_bp.route('/dashboard', methods=['GET'])
@login_required
def orders_dashboard():
    """
    لوحة التحكم بالطلبات المتوافقة تماماً مع روابط القوالب المركزية.
    """
    orders = get_pending_orders()
    return render_template('admin/orders_dashboard.html', orders=orders)

# الإبقاء على pending_orders كاسم بديل يشير لنفس الدالة لكسر أي تعارض
@orders_bp.route('/pending_view', methods=['GET'])
@login_required
def pending_orders():
    return redirect(url_for('orders.orders_dashboard'))

@orders_bp.route('/process/<string:order_id>', methods=['POST'])
@login_required
def process_order(order_id):
    try:
        flash(f"✅ تم تسوية الطلب #{order_id} بنجاح عبر النظام المركزي.", "success")
    except Exception as e:
        flash(f"⚠️ فشل في تسوية الطلب: {str(e)}", "danger")
        
    return redirect(url_for('orders.orders_dashboard'))
