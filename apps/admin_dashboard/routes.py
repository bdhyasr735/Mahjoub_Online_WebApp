# coding: utf-8
# ⚙️ محرك لوحة التحكم السيادية - منصة محجوب أونلاين 2026

from flask import render_template
from flask_login import login_required, current_user
from . import admin_dashboard
from apps.models.supplier_db import Supplier

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    """
    عرض لوحة القيادة (Dashboard) الرئيسية.
    """
    try:
        # إحصائية بسيطة لشركاء النجاح
        total_suppliers = Supplier.query.count()
        
        # تصحيح: تم إغلاق القوس بنجاح هنا
        stats = {
            'total_suppliers': total_suppliers,
            'system_health': '100% مستقر'
        } 
        
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               stats=stats)
    except Exception as e:
        return f"خطأ في تحميل مركز القيادة: {str(e)}", 500

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    """
    إعدادات النظام السيادية
    """
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers', methods=['GET'])
@login_required
def list_suppliers():
    """
    قائمة الموردين المعتمدين
    """
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
