# -*- coding: utf-8 -*-
# 📂 apps/suppliers_dashboard/registry.py

MODULES_REGISTRY = {
    'supplier_wallet': {
        'title': 'المحفظة والمالية',
        'icon': 'fas fa-wallet',
        'links': {
            'supplier_wallet_bp.wallet_dashboard_redirect': 'حركة المحفظة',
            'supplier_wallet_bp.withdraw_redirect': 'سحب الرصيد'
        }
    }
}
