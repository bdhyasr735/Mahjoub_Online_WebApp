# coding: utf-8
import traceback
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# استيراد النماذج
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# تعريف الـ Blueprint بالاسم المطابق للـ Endpoint المطلوب
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin' # إضافة الـ prefix هنا يقلل التضارب
)

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الإدارة المركزية"""
    try:
        # فحص صلاحية الوصول
        if not isinstance(current_user, AdminUser):
            flash("عذراً، هذه المنطقة مخصصة للمدراء فقط.", "danger")
            return redirect(url_for('auth_portal.login'))

        # جلب البيانات
        total_suppliers = Supplier.query.count()
        
        return render_template(
            'admin/dashboard_content.html',
            total_suppliers=total_suppliers,
            total_balance_sar=0.0,
            total_balance_yer=0.0,
            total_balance_usd=0.0,
            recent_transactions=[]
        )
        
    except Exception as e:
        print(f"🚨 [CRITICAL ERROR] Template Loading Failed: {traceback.format_exc()}")
        return f"حدث خطأ فني: {str(e)}", 500

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    """عرض قائمة الموردين"""
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    try:
        suppliers = Supplier.query.all()
        return render_template('admin/suppliers.html', suppliers=suppliers)
    except Exception as e:
        print(f"🚨 [CRITICAL ERROR] Suppliers Page Failed: {traceback.format_exc()}")
        return "حدث خطأ في تحميل قائمة الموردين", 500
