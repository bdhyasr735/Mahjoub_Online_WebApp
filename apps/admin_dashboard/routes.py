# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, session, abort
from flask_login import login_required, current_user

# 1. تعريف البلوبرينت (تأكد أن المتغير اسمه 'admin_dashboard' ليتطابق مع registry.py)
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

def admin_required():
    """دالة مساعدة للتحقق من أن المستخدم مدير نظام."""
    if session.get('user_type') != 'admin':
        abort(403) # منع الوصول لغير المدراء

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المسؤول الرئيسية.
    المسار النهائي سيكون: /admin/dashboard
    """
    admin_required()
    
    # بيانات تجريبية (يتم تحديثها لاحقاً باستعلامات قاعدة البيانات)
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
    المسار النهائي سيكون: /admin/settings
    """
    admin_required()
    return render_template('admin/settings.html')
