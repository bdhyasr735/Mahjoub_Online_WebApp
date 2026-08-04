# coding: utf-8
# 📂 apps/admin_orders/routes/actions.py

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.orders_db import Order

# تعريف الـ Blueprint الخاص بالإجراءات أو العمليات على الطلبات
actions_bp = Blueprint('admin_order_actions', __name__, url_prefix='/admin/orders/actions')

@actions_bp.route('/update-status/<string:order_id>', methods=['POST'])  # ✅ غير int إلى string لأن order_id نصي
@login_required
def update_status(order_id):
    """تحديث حالة الطلب (قيد المعالجة، تم الشحن، ملغي، إلخ)"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status:
        try:
            order.status = new_status
            db.session.commit()
            flash('تم تحديث حالة الطلب بنجاح.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء التحديث: {str(e)}', 'danger')
    else:
        flash('لم يتم تحديد حالة صحيحة.', 'warning')
    
    # ✅ استخدم admin_orders_bp.view_admin_order
    return redirect(url_for('admin_orders_bp.view_admin_order', order_id=order.id))

@actions_bp.route('/delete/<string:order_id>', methods=['POST'])  # ✅ غير int إلى string
@login_required
def delete_order(order_id):
    """حذف طلب من لوحة الإدارة"""
    order = Order.query.get_or_404(order_id)
    try:
        db.session.delete(order)
        db.session.commit()
        flash('تم حذف الطلب بنجاح.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل حذف الطلب: {str(e)}', 'danger')
    
    # ✅ استخدم admin_orders_bp.list_admin_orders
    return redirect(url_for('admin_orders_bp.list_admin_orders'))
