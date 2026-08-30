# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/registry.py

MODULE_NAME = "بوابة الموردين"
MODULE_ICON = "fa-store"
SHOW_IN_SUPPLIER = True

LINKS = {
    "suppliers_bp.dashboard": "لوحة التحكم",
}

def register_module(app):
    """تسجيل موديول بوابة الموردين في التطبيق الرئيسي."""
    from apps.suppliers_auth_portal.routes import suppliers_bp
    if 'suppliers_bp' not in app.blueprints:
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
