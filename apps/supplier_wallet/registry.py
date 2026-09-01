# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# الروابط المباشرة التي يتعامل معها القالب الجانبي كقاموس (Links Dictionary)
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

# عناصر القائمة المنسدلة بدون أي عناصر فارغة أو مربكة
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
    """
    تسجيل موديول المحفظة بالهيكلية القياسية النظيفة لمنع ظهور أي نصوص أو أزرار وهمية
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
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }

    # تسجيل الموديول تحت المفتاحين لمنع ظهور النصوص الخام
    app.supplier_modules['supplier_wallet'] = module_payload
    app.supplier_modules['suppliers_product'] = module_payload
    print("🟢 [التسجيل الديناميكي]: ✅ تم تحميل وتسجيل الموديول 'supplier_wallet' بنجاح.")
