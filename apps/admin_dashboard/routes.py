# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template
from flask_login import login_required

# تعريف البلوبرينت الخاص بالإدارة
# الاسم 'admin_dashboard' هو المرجع الأساسي في url_for
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
    بفضل تسجيل الموديول بـ url_prefix='/admin'،
    سيصبح المسار النهائي: /admin/dashboard
    """
    return render_template('admin/dashboard.html')

@admin_dashboard.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    إعدادات النظام العامة.
    المسار النهائي: /admin/settings
    """
    return render_template('admin/settings.html')
