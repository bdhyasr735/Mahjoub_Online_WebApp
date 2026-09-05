# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

MODULE_NAME = "لوحة تحكم الموردين"
DISPLAY_NAME = "لوحة تحكم الموردين"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True
IS_LAYOUT_CONTAINER = False

NAV_ITEMS = [
    {
        'endpoint': 'suppliers_dashboard.dashboard',
        'title': 'الرئيسية'
    }
]

def register_module(app):
    """دالة تسجيل الموديول الديناميكي"""
    try:
        from apps.suppliers_dashboard.routes import suppliers_dashboard_bp
        if 'suppliers_dashboard_bp' not in app.blueprints:
            app.register_blueprint(suppliers_dashboard_bp)
            logger.info("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
    except Exception as e:
        logger.error(f"❌ [Registry]: فشل تسجيل موديول 'suppliers_dashboard': {e}")

class SuppliersDashboardRegistry:
    def __init__(self, app=None):
        self.modules = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        logger.info("تم تهيئة مسجل لوحة الموردين (SuppliersDashboardRegistry) بنجاح.")

    def register_module_config(self, key, config):
        if key in self.modules:
            logger.warning(f"الموديول '{key}' مسجل مسبقاً، سيتم تحديثه.")
        self.modules[key] = config

    def get_modules(self):
        return self.modules

suppliers_registry = SuppliersDashboardRegistry()
