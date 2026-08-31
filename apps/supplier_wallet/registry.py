# coding: utf-8

MODULE_NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
ICON = "wallet"  # أو أي أيقونة معتمدة لديك
SHOW_IN_SUPPLIER = True
SORT_ORDER = 20

# تعريف الروابط التي ستظهر في القائمة الجانبية للمورد
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
