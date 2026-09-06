# 📂 apps/supplier_wallet/registry.py

MODULE_KEY = "supplier_wallet"
DISPLAY_NAME = "المحفظة الرقمية"
MODULE_ICON = "fas fa-wallet"

# ✅ تأكد من تفعيل هذا الخيار لظهوره في بوابة الموردين
SHOW_IN_SUPPLIER = True 
SHOW_IN_ADMIN = False

LINKS = {
    "supplier_wallet.index": "المحفظة الرئيسية",
    "supplier_wallet.transactions": "حركات الحساب"
}

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "title": DISPLAY_NAME,
        "icon": MODULE_ICON,
        "show_in_supplier": SHOW_IN_SUPPLIER,
        "links": LINKS  # يجب أن يكون dict
    }
