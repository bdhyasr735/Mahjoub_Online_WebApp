# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
# ملاحظة: يمكنك استيراد الموديلات هنا لاحقاً لجلب البيانات الحقيقية
# from apps.models import Supplier, OrderFinancial 

# تعريف البلوبرينت الخاص بالإدارة
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المسؤول الرئيسية.
    المسار النهائي: /admin/dashboard
    يتم استدعاء القالب من المجلد الفرعي 'admin/' داخل الـ templates.
    """
    # يمكنك لاحقاً استبدال هذه القيم ببيانات حقيقية من قاعدة البيانات
    context = {
        'total_suppliers': 0,
        'total_balance_sar': 0.00,
        'total_balance_yer': 0.00,
        'total_balance_usd': 0.00,
        'recent_transactions': []
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_dashboard.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    إعدادات النظام العامة.
    المسار النهائي: /admin/settings
    """
    return render_template('admin/settings.html')
