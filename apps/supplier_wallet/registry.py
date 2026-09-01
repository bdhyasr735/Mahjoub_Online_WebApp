# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف الروابط الثابتة كمرجع آمن (Fallback & Static Definitions) لتجنب أخطاء السياق أثناء الإقلاع
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'لوحة التحكم',
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'title': 'لوحة التحكم',
        'icon': 'fas fa-chart-pie'
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
    """
    تسجيل موديول المحفظة في التطبيق الرئيسي بأمان تام دون انتهاك سياق التطبيق
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
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }

    # تسجيل الموديول تحت كلا المفتاحين لتوافق القالب الجانبي تماماً
    app.supplier_modules['supplier_wallet'] = module_payload
    app.supplier_modules['suppliers_product'] = module_payload
    print("🟢 [التسجيل الديناميكي]: ✅ تم تحميل وتسجيل الموديول 'supplier_wallet' بنجاح.")
