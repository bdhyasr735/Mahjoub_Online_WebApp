# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_treasury"
MODULE_NAME = "الرقابة المالية"
DISPLAY_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-wallet"
ICON = "landmark"
VERSION = "2.4.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"
SHOW_IN_ADMIN = True

LINKS = {
    "admin_treasury.treasury_index": "لوحة الخزينة والقيود المركزية",
    "suppliers_wallets_controller.index": "إدارة محافظ الموردين",
    "suppliers_wallets_controller.withdraw_requests_list": "طلبات السحب"
}

links = LINKS

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": [],
        "links": links
    }

def register_module(app):
    try:
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
            
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        if "admin_suppliers_wallets" not in app.blueprints:
            app.register_blueprint(wallets_bp)
            print("✅ [Registry]: تم تسجيل موديول 'محافظ الموردين' بنجاح.")
            
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل الموديولات: {e}")
