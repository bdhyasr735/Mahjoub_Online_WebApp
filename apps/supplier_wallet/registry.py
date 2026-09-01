# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from flask import url_for

MODULE_NAME = "محفظة الموردين"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.wallet_transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw_request': 'سحب الرصيد'
}

def register_module(app):
    from apps.supplier_wallet.routes import wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")

    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
    
    # ✅ هيكل مبسط - إدارة المالية مع قوائم فرعية مباشرة (بدون محفظة الموردين كعنصر وسيط)
    finance_module = {
        'name': 'إدارة المالية',
        'title': 'إدارة المالية',
        'icon': 'fas fa-coins',
        'url': '#',
        'is_finance': True,
        'submenu': [
            {
                'name': 'حركة المحفظة',
                'title': 'حركة المحفظة',
                'icon': 'fas fa-exchange-alt',
                'url': '/supplier/wallet/general/transactions',
                'endpoint': 'supplier_wallet.wallet_transactions'
            },
            {
                'name': 'سحب الرصيد',
                'title': 'سحب الرصيد',
                'icon': 'fas fa-money-bill-wave',
                'url': '/supplier/wallet/general/withdraw',
                'endpoint': 'supplier_wallet.withdraw_request'
            }
        ]
    }
    
    # إضافة موديول إدارة المالية
    app.supplier_modules['إدارة المالية'] = finance_module
    
    # حذف المفتاح القديم
    if 'supplier_wallet' in app.supplier_modules:
        del app.supplier_modules['supplier_wallet']
    
    print("🟢 [التسجيل الديناميكي]: ✅ تم تسجيل 'إدارة المالية' مع القوائم الفرعية في لوحة المورد.")
