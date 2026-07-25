# coding: utf-8
# 📂 apps/admin_dashboard/registry.py

from flask import url_for

MODULE_NAME = "لوحة التحكم الرئيسية"
MODULE_ICON = "fa-tachometer-alt"
SHOW_IN_SUPPLIER = False

LINKS = {
    "📊 الرئيسية": "admin_dashboard_bp.dashboard"
}

def register_module(app):
    try:
        from apps.admin_dashboard.routes import admin_dashboard_bp
        if 'admin_dashboard_bp' not in app.blueprints:
            app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
            print("✅ [Registry]: تم تسجيل موديول لوحة التحكم الرئيسية بنجاح.")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل admin_dashboard: {e}")
    return app

def get_module_link():
    return url_for('admin_dashboard_bp.dashboard')

__all__ = [
    'MODULE_NAME', 'MODULE_ICON', 'SHOW_IN_SUPPLIER', 'LINKS',
    'register_module', 'get_module_link'
]
