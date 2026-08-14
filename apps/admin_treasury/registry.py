# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_treasury"
DISPLAY_NAME = "الرقابة المالية"
ICON = "landmark"
VERSION = "2.4.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"

NAV_ITEMS = [
    {
        "id": "treasury_overview",
        "title": "إدارة الخزينة والقيود",
        "endpoint": "admin_treasury.treasury_index",
        "icon": "wallet",
        "permission": "view_treasury"
    }
]

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": NAV_ITEMS
    }

def register_module(app):
    """
    دالة التسجيل القياسية المعتمدة في مشروع محجوب أونلاين لموديول الرقابة المالية
    """
    from apps.admin_treasury import admin_treasury_bp
    
    if 'admin_treasury' not in app.blueprints:
        app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
