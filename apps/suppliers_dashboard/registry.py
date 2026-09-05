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
    """دالة احتياطية للتسجيل التلقائي إن طلبها النظام"""
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
