# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp

MODULE_NAME = "لوحة تحكم الموردين"
DISPLAY_NAME = "لوحة تحكم الموردين"
MODULE_ICON = "fa-chart-pie"
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        'title': 'لوحة التحكم',
        'endpoint': 'suppliers_dashboard.index'
    }
]

LINKS = {
    'suppliers_dashboard.index': 'لوحة تحكم الموردين'
}

def register_module(app):
    """تسجيل موديول لوحة تحكم الموردين ديناميكياً"""
    if suppliers_dashboard_bp.name not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp)
        print(f"✅ [Registry Supplier]: تم تسجيل موديول لوحة تحكم الموردين بنجاح.")

def init_app(app):
    pass
