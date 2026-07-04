# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, current_app
from flask_login import login_required

# 1. إنشاء الـ Blueprint
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# 2. تعريف المسار (Route)
@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    عرض لوحة تحكم النظام الرئيسية مع جلب الموديولات المسجلة من الـ Application.
    """
    
    # جلب الموديولات المسجلة مع التأكد من وجودها كقاموس لتفادي أي أخطاء
    registered_modules = getattr(current_app, 'REGISTERED_MODULES', {})
    
    # تهيئة البيانات الأساسية (سيتم استبدال القيم ببيانات حقيقية من قاعدة البيانات لاحقاً)
    context = {
        "total_suppliers": 0,
        "total_balance_sar": 0.00,
        "total_balance_yer": 0.00,
        "total_balance_usd": 0.00,
        "recent_transactions": [],
        "registered_modules": registered_modules
    }
    
    return render_template('admin/dashboard.html', **context)
