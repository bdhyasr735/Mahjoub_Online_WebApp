# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - النسخة النهائية الموثوقة

import os
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import traceback

# استيراد النماذج
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint
# ملاحظة: template_folder='templates' تعني أن Flask ستبحث عن أي قالب داخل مجلد templates
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الإدارة المركزية"""
    try:
        # فحص صلاحية الوصول
        if not getattr(current_user, 'is_admin', False) and not isinstance(current_user, AdminUser):
            return redirect(url_for('auth_portal.login'))

        total_suppliers = Supplier.query.count()
        
        # عند استخدام template_folder='templates'، المسار يبدأ من داخل هذا المجلد.
        # بما أن ملفك موجود في 'apps/admin_dashboard/templates/admin/dashboard.html'
        # فإن الطلب الصحيح هو 'admin/dashboard.html'
        return render_template(
            'admin/dashboard.html',
            total_suppliers=total_suppliers,
            total_balance_sar=0.0,
            total_balance_yer=0.0,
            total_balance_usd=0.0,
            recent_transactions=[]
        )
        
    except Exception as e:
        # طباعة الخطأ الكامل في الـ Logs لتسهيل التصحيح
        print(f"🚨 [CRITICAL ERROR] {traceback.format_exc()}")
        return f"حدث خطأ في تحميل الواجهة: {str(e)}", 500

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    """عرض قائمة الموردين"""
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    suppliers = Supplier.query.all()
    # المسار: templates/admin/suppliers.html
    return render_template('admin/suppliers.html', suppliers=suppliers)
