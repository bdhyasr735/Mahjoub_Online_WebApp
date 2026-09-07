# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_KEY = "supplier_wallet"
MODULE_NAME = "المحفظة الرقمية"
DISPLAY_NAME = "المحفظة الرقمية"
MODULE_ICON = "fas fa-wallet"
VERSION = "1.0.0"
URL_PREFIX = "/supplier/wallet"

SHOW_IN_SUPPLIER = True
SHOW_IN_ADMIN = False

# ✅ حصر الروابط بخيارين فقط: حركة المحفظة وسحب الرصيد
LINKS = {
    "supplier_wallet_bp.transactions_redirect": "حركة المحفظة",
    "supplier_wallet_bp.withdraw_redirect": "سحب الرصيد"
}

links = LINKS


def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "title": DISPLAY_NAME,
        "icon": MODULE_ICON,
        "url": URL_PREFIX,
        "show_in_supplier": SHOW_IN_SUPPLIER,
        "show_in_admin": SHOW_IN_ADMIN,
        "links": LINKS,
        "items": []
    }
