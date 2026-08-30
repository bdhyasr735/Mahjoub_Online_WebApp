# apps/admin_permissions/registry.py

from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

# تعريف الموديول
MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fa-shield-alt"
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {'title': 'إدارة الصلاحيات', 'endpoint': 'admin_permissions.index', 'icon': 'fa-shield-alt'},
]

def register_module(app):
    """تسجيل الموديول في التطبيق"""
    try:
        from .routes import admin_permissions_bp
        app.register_blueprint(admin_permissions_bp)
        logger.info(f"✅ تم تسجيل موديول '{MODULE_NAME}' بنجاح.")
        return True
    except Exception as e:
        logger.error(f"❌ فشل تسجيل موديول '{MODULE_NAME}': {e}")
        return False
