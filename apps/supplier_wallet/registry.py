# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

NAV_ITEMS = {
    'supplier_wallet': {
        'title': 'المحفظة المالية',
        'icon': 'fas fa-wallet',
        'order': 3,
        'links': {
            'supplier_wallet.wallet_dashboard': 'لوحة المحفظة والعمليات',
            'supplier_wallet.withdraw': 'طلب سحب رصيد'
        }
    }
}
