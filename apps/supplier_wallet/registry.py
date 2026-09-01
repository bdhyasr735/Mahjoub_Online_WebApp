# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet import supplier_wallet_bp

MODULE_NAME = "الإدارة المالية"
ICON = "wallet"
SHOW_IN_SUPPLIER = True

# القائمة الفرعية التي تظهر عند النقر على القائمة المنسدلة
SUB_ITEMS = [
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

# دعم المتغيرات المختلفة التي قد يطلبها قالب الشريط الجانبي في النظام
MENU_ITEMS = SUB_ITEMS
NAV_ITEMS = SUB_ITEMS
LINKS = SUB_ITEMS
sub_items = SUB_ITEMS

def get_menu_items():
    return SUB_ITEMS

def register_module(app):
    """تسجيل بلوبرنت الإدارة المالية بشكل آمن وتلافي أي أخطاء"""
    try:
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp)
    except Exception as e:
        print(f"⚠️ [خطأ تسجيل موديول المحفظة]: {e}")
