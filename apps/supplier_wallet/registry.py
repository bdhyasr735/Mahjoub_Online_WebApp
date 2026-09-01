# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# الروابط المباشرة بصيغة مسارات تمنع أي خطأ في توليد الـ url_for داخل القالب
LINKS = {
    '/supplier/wallet/general/transactions': 'حركة المحفظة',
    '/supplier/wallet/general/withdraw': 'سحب الرصيد'
}

MENU_ITEMS = [
    {
        'url': '/supplier/wallet/general/transactions',
        'title': 'حركة المحفظة',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'url': '/supplier/wallet/general/withdraw',
        'title': 'سحب الرصيد',
        'icon': 'fas fa-money-bill-wave'
    }
]

def register_module(app):
    """
    تسجيل موديول المحفظة مع روابط مسارات مباشرة لتفادي مشاكل الـ BuildError في القالب الجانبي
    """
    from apps.supplier_wallet.routes import wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")

    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    module_payload = {
        'name': MODULE_NAME,
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'url': '/supplier/wallet/general/',
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }

    # تسجيل الموديول تحت كلا المفتاحين لضمان ظهوره بغض النظر عن المفتاح الذي يناديه القالب
    app.supplier_modules['supplier_wallet'] = module_payload
    app.supplier_modules['suppliers_product'] = module_payload
    print("🟢 [التسجيل الديناميكي]: ✅ تم تحميل وتسجيل الموديول 'supplier_wallet' بنجاح.")
