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
    عرض لوحة تحكم النظام الرئيسية مع تمرير حالة الموديولات للقالب.
    """
    
    # استخراج قائمة الموديولات المسجلة لتمريرها للقالب (لحل مشكلة الـ Blueprint checks)
    # نستخدم current_app للوصول إلى إعدادات التطبيق
    registered_modules = {
        'admin_suppliers_list': 'suppliers_bp' in current_app.blueprints,
        'finance_module': 'treasury_bp' in current_app.blueprints
    }
    
    context = {
        "total_suppliers": 0,
        "total_balance_sar": 0.00,
        "total_balance_yer": 0.00,
        "total_balance_usd": 0.00,
        "recent_transactions": [],
        "registered_modules": registered_modules
    }
    
    # تأكد أن الملف موجود في: apps/admin_dashboard/templates/admin/dashboard.html
    return render_template('admin/dashboard.html', **context)
