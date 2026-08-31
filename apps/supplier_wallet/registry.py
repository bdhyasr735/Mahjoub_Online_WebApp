# coding: utf-8

MODULE_NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
ICON = "wallet"
SHOW_IN_SUPPLIER = True
SORT_ORDER = 20

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
