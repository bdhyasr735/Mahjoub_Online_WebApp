# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

# ضروري ليظهر في بوابة الموردين
SHOW_IN_SUPPLIER = True

NAV_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard',
        'title': 'لوحة المحفظة والعمليات'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'طلب سحب رصيد'
    }
]

MODULE_NAME = "المحفظة المالية"
MODULE_ICON = "fas fa-wallet"
