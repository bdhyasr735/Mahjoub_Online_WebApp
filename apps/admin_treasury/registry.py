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

# ✅ استخدام Endpoints نظامية موحدة ومترابطة تماماً
LINKS = {
    "admin_treasury.treasury_index": "لوحة الخزينة والقيود المركزية",
    "admin_suppliers_wallets.index": "إدارة محافظ الموردين",
    "admin_suppliers_wallets.withdraw_requests_list": "طلبات السحب"
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
        # 1. تسجيل موديول الخزينة المركزية بالبادئة الخاصة به
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
            
        # 2. تسجيل موديول محافظ الموردين وطلبات السحب بنفس المعيار والبادئة الإدارية
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        if "admin_suppliers_wallets" not in app.blueprints:
            app.register_blueprint(wallets_bp, url_prefix="/admin/suppliers-wallets")
            print("✅ [Registry]: تم تسجيل موديول 'محافظ الموردين وطلبات السحب' بنجاح.")

        # 🔍 طباعة الـ Endpoints للتحقق من تطابقها في السجلات
        admin_wallets_endpoints = [p for p in app.view_functions.keys() if 'admin_suppliers_wallets' in p]
        print(f"🔍 [Debug Admin Wallets Endpoints]: {admin_wallets_endpoints}")
            
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
