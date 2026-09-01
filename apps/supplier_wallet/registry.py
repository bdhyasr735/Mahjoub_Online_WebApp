# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ تعريف الروابط مع مسارات افتراضية أو عامة لضمان ظهورها في القائمة الجانبية فوراً
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'حركة المحفظة وسحب الرصيد',
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'title': 'الإدارة المالية والمحفظة',
        'icon': 'fas fa-wallet'
    },
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
    # ✅ استيراد وتسجيل البلوبرنت لضمان إتاحة الـ Endpoints
    from apps.supplier_wallet.routes import wallet_bp as supplier_wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")

    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    # تسجيل الموديول بالهيكلية الشاملة التي تتوافق مع نظام القوائم الجانبية
    app.supplier_modules['supplier_wallet'] = {
        'name': MODULE_NAME,
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER,
        'url': 'supplier_wallet.wallet_dashboard_redirect'
    }
