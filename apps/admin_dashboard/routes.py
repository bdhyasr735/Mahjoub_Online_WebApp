# coding: utf-8
# ⚙️ محرك لوحة التحكم السيادية - منصة محجوب أونلاين 2026

from flask import render_template
from flask_login import login_required, current_user
# استيراد البلوبرينت الموحد لهذا المحرك
from . import admin_dashboard
from apps.models.supplier_db import Supplier

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    """
    عرض لوحة القيادة (Dashboard) مع الإحصائيات الحيوية.
    المسار المعتمد: apps/admin_dashboard/templates/admin/dashboard_content.html
    """
    try:
        total_suppliers = Supplier.query.count()
        stats = {
            'total_suppliers': total_suppliers,
            'active_orders': 0,
            'system_health': '100% مستقر'
        }
        # استدعاء ملف المحتوى الذي يرث من admin_base.html
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               stats=stats)
    except Exception as e:
        # في حال حدوث خطأ، سيظهر رسالة واضحة في المتصفح للتشخيص
        return f"خطأ في تحميل مركز القيادة: {str(e)}", 500

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    """
    إعدادات النظام السيادية
    """
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers/list', methods=['GET'])
@login_required
def list_suppliers():
    """
    قائمة الموردين المعتمدين
    """
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
