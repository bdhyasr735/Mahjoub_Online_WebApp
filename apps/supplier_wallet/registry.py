# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ الروابط المعرفة مباشرة بدون استيرادات خارجية في أعلى الملف لتجنب الاستيراد الدائري
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.transactions',
        'title': 'حركة المحفظة',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'سحب الرصيد',
        'icon': 'fas fa-money-bill-wave'
    }
]

def register_module(app):
    # ✅ يتم استيراد البلوبرنت هنا محلياً داخل الدالة لكسر حلقة الاستيراد الدائري نهائياً
    from apps.supplier_wallet.routes import wallet_bp as supplier_wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")

    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    app.supplier_modules['supplier_wallet'] = {
        'name': MODULE_NAME,
        'icon': MODULE_ICON,
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }
