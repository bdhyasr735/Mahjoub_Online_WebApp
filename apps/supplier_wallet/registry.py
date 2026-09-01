# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
ICON = "wallet"
SHOW_IN_SUPPLIER = True

MENU_ITEMS = [
    {
        "title": "لوحة المحفظة",
        "name": "لوحة المحفظة",
        "endpoint": "supplier_wallet.wallet_dashboard",
        "icon": "dashboard"
    },
    {
        "title": "كشف حركات المحفظة",
        "name": "كشف حركات المحفظة",
        "endpoint": "supplier_wallet.transactions",
        "icon": "list"
    },
    {
        "title": "طلب سحب الرصيد",
        "name": "طلب سحب الرصيد",
        "endpoint": "supplier_wallet.withdraw",
        "icon": "cash"
    }
]

NAV_ITEMS = MENU_ITEMS
LINKS = MENU_ITEMS

def get_menu_items():
    return MENU_ITEMS

def get_modules():
    """إرجاع بيانات الموديول ليتم توافقها مع أي نظام استدعاء مركزي"""
    return {
        "module_name": MODULE_NAME,
        "icon": ICON,
        "show_in_supplier": SHOW_IN_SUPPLIER,
        "menu_items": MENU_ITEMS
    }

def register_module(app):
    """تسجيل بلوبرنت الإدارة المالية بشكل آمن وتلافي أي أخطاء استيراد"""
    try:
        from apps.supplier_wallet.routes import wallet_bp
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(wallet_bp)
    except ImportError:
        try:
            from apps.supplier_wallet.routes import supplier_wallet_bp
            if 'supplier_wallet' not in app.blueprints:
                app.register_blueprint(supplier_wallet_bp)
        except Exception as e:
            print(f"⚠️ [تحذير تسجيل موديول المحفظة]: {e}")
