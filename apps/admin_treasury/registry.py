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

# ✅ استخدام Endpoints نظامية تحتوي على نقطة (.) لكي يتجاوزها شرط القالب بنجاح
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
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
            
        # تسجيل موديول محافظ الموردين بالاسم الأساسي ليتطابق مع الـ Endpoints
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        if "admin_suppliers_wallets" not in app.blueprints:
            app.register_blueprint(wallets_bp)
            print("✅ [Registry]: تم تسجيل موديول 'محافظ الموردين' بنجاح.")

        # 🔍 طباعة الـ Endpoints المسجلة التي تحتوي على كلمة withdraw للتأكد منها في سجلات ريندر
        withdraw_endpoints = [p for p in app.view_functions.keys() if 'withdraw' in p]
        print(f"🔍 [Debug Endpoints]: {withdraw_endpoints}")
            
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
