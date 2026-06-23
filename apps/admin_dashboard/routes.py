# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - النسخة النهائية الموثوقة

import os
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import traceback

# استيراد النماذج
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# تعريف المسار المطلق لمجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates' # Flask ستبحث داخل مجلد 'templates' تلقائياً
)

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    try:
        # فحص صلاحية الوصول
        if not getattr(current_user, 'is_admin', False) and not isinstance(current_user, AdminUser):
            return redirect(url_for('auth_portal.login'))

        total_suppliers = Supplier.query.count()
        
        # بما أننا حددنا template_folder='templates'
        # وبما أن مسارك هو: templates/admin/dashboard.html
        # فإن المسار الصحيح للطلب هو 'admin/dashboard.html'
        return render_template(
            'admin/dashboard.html',
            total_suppliers=total_suppliers,
            total_balance_sar=0.0,
            total_balance_yer=0.0,
            total_balance_usd=0.0,
            recent_transactions=[]
        )
        
    except Exception as e:
        print(f"🚨 [CRITICAL ERROR] {traceback.format_exc()}")
        return "حدث خطأ في تحميل الواجهة", 500

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
