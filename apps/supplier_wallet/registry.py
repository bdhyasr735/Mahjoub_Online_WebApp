# coding: utf-8

MODULE_NAME = "الإدارة المالية"
ICON = "wallet"
SHOW_IN_SUPPLIER = True

# تعريف العناصر بالطريقة التي يبحث عنها __init__.py ديناميكياً
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

# توافقاً مع فحص __init__.py (LINKS أو NAV_ITEMS أو get_menu_items)
NAV_ITEMS = MENU_ITEMS

def get_menu_items():
    return MENU_ITEMS

def register_module(app):
    """تسجيل بلوبرنت الإدارة المالية"""
    from apps.supplier_wallet.routes import supplier_wallet_bp
    app.register_blueprint(supplier_wallet_bp)
