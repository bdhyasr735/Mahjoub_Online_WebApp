# -*- coding: utf-8 -*-
from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

MODULE_NAME = "لوحة تحكم المورد"
MODULE_ICON = "fas fa-tachometer-alt"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        "endpoint": "suppliers_dashboard.dashboard",
        "title": "الرئيسية",
        "icon": "fas fa-home"
    }
]

def register_module(app):
    """دالة التسجيل التلقائي المطلوبة في التطبيق الرئيسي"""
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print("✅ [تسجيل الموديول]: تم تسجيل لوحة تحكم الموردين بنجاح عبر registry.py")
