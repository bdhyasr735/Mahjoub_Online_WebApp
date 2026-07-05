# coding: utf-8
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from apps.models.orders_db import Order
from apps.models.supplier_db import Supplier

suppliers_orders_bp = Blueprint('suppliers_orders', __name__, template_folder='templates')

@suppliers_orders_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الطلبات - محسنة لتناسب الموردين، الملاك، والموظفين"""
    page = request.args.get('page', 1, type=int)
    
    # تحديد معرف المورد بناءً على هوية المستخدم المسجل
    if session.get('user_type') == 'supplier':
        target_supplier_id = current_user.id
    else:
        target_supplier_id = getattr(current_user, 'supplier_id', None)

    # التحقق من أن المستخدم لديه صلاحية الوصول
    if not target_supplier_id:
        return "غير مصرح لك بالوصول", 403

    # بناء الاستعلام لفلترة الطلبات الخاصة بهذا المورد فقط
    query = Order.query.filter(Order.supplier_id == target_supplier_id)
        
    # تفعيل نظام الصفحات (Pagination)
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    # دعم طلبات الـ AJAX
    # ملاحظة: تأكد من أن ملف البارتشال موجود في نفس المسار الفرعي (admin/)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/_orders_table.html', pagination=pagination)
        
    # استدعاء المسار الصحيح للملف
    return render_template('admin/suppliers_orders_dashboard.html', pagination=pagination)
