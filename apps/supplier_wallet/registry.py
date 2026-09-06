# apps/supplier_wallet/registry.py

SUPPLIER_MODULES_REGISTRY = {
    'financial_management': {
        'title': 'الإدارة المالية',
        'icon': 'fas fa-wallet',
        'links': {
            'supplier_wallet.wallet_detail': 'حركة المحفظة',
            'supplier_wallet.payout_requests': 'سحب الرصيد'
        }
    }
}
