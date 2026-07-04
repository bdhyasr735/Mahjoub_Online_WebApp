# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template
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
    عرض لوحة تحكم النظام الرئيسية.
    تم إزالة الجلب اليدوي للموديولات لأنها تُحقن تلقائياً بواسطة الـ Context Processor.
    """
    
    # تهيئة البيانات الأساسية فقط (سيتم استبدال القيم ببيانات حقيقية من قاعدة البيانات)
    context = {
        "total_suppliers": 0,
        "total_balance_sar": 0.00,
        "total_balance_yer": 0.00,
        "total_balance_usd": 0.00,
        "recent_transactions": []
    }
    
    return render_template('admin/dashboard.html', **context)
