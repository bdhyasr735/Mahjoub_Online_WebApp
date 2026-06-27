# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
# استيراد النماذج
from apps.models.orders_db import Order 
from apps.models.supplier_db import Supplier

# تعريف البلوبرينت
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

def supplier_required():
    """
    دالة تحقق أمني: تضمن أن المستخدم الحالي مورد.
    """
    if session.get('user_type') != 'supplier':
        abort(403)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة التحكم الرئيسية للمورد.
    """
    supplier_required() 
    
    # جلب عدد الطلبات المعلقة فعلياً
    pending_orders_count = Order.query.filter_by(
        supplier_id=current_user.id, 
        status='pending'
    ).count()

    return render_template('suppliers/dashboard.html', pending_orders_count=pending_orders_count)

@dashboard_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    supplier_required() 
    flash("سيتم تفعيل خدمة السحب قريباً، يرجى التواصل مع الإدارة.", "info")
    return redirect(url_for('suppliers_dashboard.dashboard'))

@dashboard_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """
    صفحة إعدادات المتجر مع جلب بيانات الملف الشخصي والمحفظة.
    """
    supplier_required() 
    
    # جلب المورد مع بيانات الملف الشخصي والمحفظة المرتبطة به لضمان عدم وجود أخطاء في القالب
    supplier_data = Supplier.query.options(
        joinedload(Supplier.supplier_profile),
        joinedload(Supplier.wallet)
    ).get(current_user.id)
    
    # إضافة تحقق بسيط للتأكد من وجود المورد
    if not supplier_data:
        abort(404)
    
    # تمرير supplier_data كـ current_user للقالب كما طلبت
    return render_template('suppliers/settings.html', current_user=supplier_data)
