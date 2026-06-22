# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - لوحة تحكم الإدارة المركزية

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
# تأكد أن هذه الموديلات موجودة في الفهرس الموحد apps/models/__init__.py
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint الخاص بالإدارة
admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم القيادة المركزية للمدير
    """
    # 1. حماية سيادية: التأكد من أن المستخدم مدير
    if not isinstance(current_user, AdminUser):
        flash("هذه المنطقة مخصصة للمدراء فقط.", "error")
        return redirect(url_for('auth_portal.login'))

    try:
        # 2. جلب إحصائيات النظام
        total_suppliers = Supplier.query.count()
        
        stats = {
            'total_suppliers': total_suppliers,
            'active_orders': 0,
            'central_balance': "0.00"
        }
        
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        print(f"DEBUG: Admin Dashboard Error: {e}")
        return "حدث خطأ أثناء تحميل لوحة التحكم", 500

@admin_dashboard.route('/settings')
@login_required
def settings():
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
    return "صفحة إعدادات النظام قيد التطوير"

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    """عرض قائمة الموردين للمدير"""
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
