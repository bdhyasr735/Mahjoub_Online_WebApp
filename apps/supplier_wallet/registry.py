# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from flask import url_for

MODULE_NAME = "إدارة المالية"
MODULE_ICON = "fas fa-coins"
SHOW_IN_SUPPLIER = True

# تعريف الروابط الداخلية للمحفظة - بنفس تنسيق LINKS الذي يتوقعه القالب
LINKS = {
    'supplier_wallet.wallet_transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw_request': 'سحب الرصيد'
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
    تسجيل موديول المحفظة كقائمة تحت إدارة المالية
    """
    from apps.supplier_wallet.routes import wallet_bp
    
    # تسجيل البلوبرنت
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")

    # التأكد من وجود قاموس الموديولات
    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
    
    # ✅ تسجيل الموديول بنفس هيكل LINKS الذي يتوقعه القالب
    module_payload = {
        'name': MODULE_NAME,
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'url': '/supplier/wallet/general/transactions',
        'links': LINKS,  # 🔥 هذا هو المهم! القالب يبحث عن links
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }
    
    # ✅ تسجيل الموديول تحت المفتاح 'إدارة المالية' (بدلاً من supplier_wallet)
    app.supplier_modules['إدارة المالية'] = module_payload
    
    # 🔥 حذف المفتاح القديم supplier_wallet إن وجد لتجنب التكرار
    if 'supplier_wallet' in app.supplier_modules:
        del app.supplier_modules['supplier_wallet']
    
    print("🟢 [التسجيل الديناميكي]: ✅ تم تسجيل 'إدارة المالية' مع الروابط:")
    for endpoint, title in LINKS.items():
        print(f"   - {title} ({endpoint})")
