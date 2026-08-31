# -*- coding: utf-8 -*-
# 📂 apps/admin_dashboard/registry.py

from flask import Blueprint, render_template
from flask_login import login_required

MODULE_NAME = "لوحة التحكم الإدارية"
MODULE_ICON = "fa-tachometer-alt"
SHOW_IN_SUPPLIER = False

# إنشاء الـ Blueprint الخاص بلوحة التحكم مع تحديد مجلد القوالب
admin_dashboard_bp = Blueprint(
    'admin_dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/dashboard'
)

@admin_dashboard_bp.route('/')
@login_required
def index():
    return render_template('admin/dashboard.html')

def register_module(app):
    """دالة التسجيل الديناميكي للوحة التحكم"""
    if admin_dashboard_bp.name not in app.blueprints:
        app.register_blueprint(admin_dashboard_bp)
    print("✅ [لوحة التحكم]: تم تسجيل موديول admin_dashboard بنجاح.")
