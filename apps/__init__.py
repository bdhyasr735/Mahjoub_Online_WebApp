# coding: utf-8
from flask import render_template, abort
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier
# نقوم باستيراد admin_dashboard من ملف __init__ الخاص بالمجلد نفسه
from apps.admin_dashboard import admin_dashboard

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    """
    مركز القيادة السيادي - المسار: /admin/dashboard
    """
    try:
        # جلب البيانات
        total_suppliers = Supplier.query.count()
        
        stats = {
            'total_suppliers': total_suppliers,
            'active_orders': 0,
            'system_health': '100% مستقر'
        }
        
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               stats=stats)
    except Exception as e:
        # طباعة الخطأ في السجلات للمساعدة في التشخيص
        print(f"Error in dashboard_home: {e}")
        return f"خطأ في تحميل مركز القيادة: {str(e)}", 500

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    """
    إعدادات السيادة
    """
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers/list', methods=['GET'])
@login_required
def list_suppliers():
    """
    سجل الموردين
    """
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
