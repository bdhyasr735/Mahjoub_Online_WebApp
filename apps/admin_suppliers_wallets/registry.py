# -*- coding: utf-8 -*-
# 📂 apps/admin_suppliers_wallets/registry.py
"""
تسجيل موديول إدارة محافظ الموردين وطلبات السحب
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_suppliers_wallets"
MODULE_NAME = "إدارة محافظ الموردين"
DISPLAY_NAME = "محافظ الموردين"
MODULE_ICON = "fas fa-wallet"
ICON = "wallet"
VERSION = "2.4.0"
URL_PREFIX = "/admin/suppliers-wallets"
REQUIRED_PERMISSION = "manage_platform_treasury"
SHOW_IN_ADMIN = False  # يظهر كروابط فرعية تحت الرقابة المالية

# ✅ تصحيح أسماء نقاط النهاية (Endpoints)
# يجب أن تتطابق مع الـ Blueprint المُسجل في __init__.py
LINKS = {
    "admin_suppliers_wallets.suppliers_wallets_controller.index": "إدارة محافظ الموردين",
    "admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list": "طلبات السحب"
}

links = LINKS

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": [],
        "links": links,
        "show_in_admin": SHOW_IN_ADMIN
    }

def register_module(app):
    try:
        # تسجيل الـ Blueprint الخاص بمحافظ الموردين وطلبات السحب
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        
        # ✅ التحقق بالاسم الصحيح للـ Blueprint الرئيسي
        if wallets_bp.name not in app.blueprints:
            app.register_blueprint(wallets_bp)
            print("✅ [Module]: تم تسجيل موديول 'admin_suppliers_wallets' بنجاح.")
        else:
            print("ℹ️ [Module]: موديول 'admin_suppliers_wallets' مُسجل مسبقاً.")
            
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول محافظ الموردين: {e}")
