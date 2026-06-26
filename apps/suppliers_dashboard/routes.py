# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# تعريف البلوبرينت
# الاسم 'suppliers_dashboard' يجب أن يتطابق مع المرجع المستخدم في الـ Templates والـ Registry
dashboard_bp = Blueprint(
    'suppliers_dashboard', 
    __name__, 
    template_folder='templates'
)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة التحكم الرئيسية للمورد.
    يتم الوصول إليها عبر: /suppliers/dashboard
    """
    # هنا سيتم جلب البيانات الحقيقية لاحقاً من قاعدة البيانات
    context = {
        'pending_orders_count': 0, # سيتم استبدالها لاحقاً بـ Order.query...
        'supplier_name': getattr(current_user, 'trade_name', 'شريكنا العزيز')
    }
    
    # تأكد أن الملف موجود في المسار: templates/suppliers/dashboard.html
    return render_template('suppliers/dashboard.html', **context)

@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    صفحة إعدادات المتجر الخاصة بالمورد.
    """
    return render_template('suppliers/settings.html')
