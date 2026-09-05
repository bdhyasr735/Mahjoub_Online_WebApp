# -*- coding: utf-8 -*-

import os
from flask import Blueprint, render_template

# إنشاء Blueprint لوحة تحكم الموردين مع تحديد مجلد القوالب والمسار الأساسي
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/supplier'
)

@suppliers_dashboard_bp.route('/dashboard')
def supplier_dashboard_index():
    """الصفحة الرئيسية للوحة تحكم الموردين"""
    from flask_login import current_user
    return render_template('suppliers_dashboard/dashboard.html', current_user=current_user)

def register_module(app):
    """دالة التسجيل الديناميكي للموديول في التطبيق الرئيسي"""
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
    print("✅ [لوحة تحكم الموردين]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
