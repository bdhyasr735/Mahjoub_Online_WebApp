# coding: utf-8
from flask import render_template
from flask_login import login_required, current_user
# استيراد البلوبرينت المعرف في __init__.py الخاص بهذا المجلد
from . import admin_dashboard
from apps.models.supplier_db import Supplier

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    """
    مركز القيادة: عرض الإحصائيات العامة للمنصة
    """
    try:
        total_suppliers = Supplier.query.count()
        stats = {
            'total_suppliers': total_suppliers,
            'active_orders': 0,
            'system_health': '100% مستقر'
        }
        # المسار الآن يشير إلى مجلد admin داخل مجلد templates الخاص بالـ blueprint
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               stats=stats)
    except Exception as e:
        # رسالة الخطأ هنا ستظهر في المتصفح إذا حدث فشل في تحميل القالب أو قاعدة البيانات
        return f"خطأ في تحميل مركز القيادة: {str(e)}", 500

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    # التأكد من وجود ملف settings.html في apps/admin_dashboard/templates/admin/
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers/list', methods=['GET'])
@login_required
def list_suppliers():
    # التأكد من وجود ملف suppliers.html في apps/admin_dashboard/templates/admin/
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
