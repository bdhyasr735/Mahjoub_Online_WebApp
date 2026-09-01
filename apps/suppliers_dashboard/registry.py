# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

MODULE_NAME = "لوحة تحكم الموردين"
DISPLAY_NAME = "لوحة تحكم الموردين"
MODULE_ICON = "fa-chart-pie"
# الإبقاء على الوصف الهيكلي فقط وعدم معاملتها كقائمة تظهر بشكل متكرر
IS_LAYOUT_CONTAINER = True

def register_module(app):
    """تسجيل الإطار الهيكلي للوحة تحكم الموردين ديناميكياً"""
    if suppliers_dashboard_bp.name not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print(f"✅ [Registry Supplier Layout]: تم تسجيل هيكل لوحة تحكم الموردين بنجاح.")

def init_app(app):
    pass
