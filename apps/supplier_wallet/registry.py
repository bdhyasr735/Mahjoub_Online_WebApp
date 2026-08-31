# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
ICON = "wallet"
SHOW_IN_SUPPLIER = True

MENU_ITEMS = [
    {
        "name": "لوحة المحفظة",
        "endpoint": "supplier_wallet.wallet_dashboard",
        "icon": "dashboard"
    },
    {
        "name": "كشف حركات المحفظة",
        "endpoint": "supplier_wallet.transactions",
        "icon": "list"
    },
    {
        "name": "طلب سحب الرصيد",
        "endpoint": "supplier_wallet.withdraw",
        "icon": "cash"
    }
]

# تغطية كافة الاحتمالات التي قد يبحث عنها نظام الـ Sidebar الرئيسي
NAV_ITEMS = MENU_ITEMS
LINKS = MENU_ITEMS
get_links = lambda: MENU_ITEMS

def get_menu_items():
    return MENU_ITEMS

def register_module(app):
    """تسجيل بلوبرنت الإدارة المالية وتجنب التكرار"""
    from apps.supplier_wallet.routes import wallet_bp
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp)
