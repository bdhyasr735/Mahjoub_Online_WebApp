# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

# ✅ استيراد البلوبرنت من ملف المسارات بالاسم الصحيح (wallet_bp) وتصديره باسم (supplier_wallet_bp)
from apps.supplier_wallet.routes import wallet_bp as supplier_wallet_bp

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ الروابط المعرفة بدقة لتتوافق مع نظام الـ Registry وقالب العرض
LINKS = {
    'supplier_wallet.wallet_dashboard_redirect': 'لوحة المحفظة',
    'supplier_wallet.transactions': 'سجل الحركات المالية',
    'supplier_wallet.withdraw': 'طلب سحب الرصيد'
}

# دعم إضافي بصيغة MENU_ITEMS لضمان التوافق المطلق مع القوالب التي تبحث عنها
MENU_ITEMS = [
    {
        'endpoint': 'supplier_wallet.wallet_dashboard_redirect',
        'title': 'لوحة المحفظة',
        'icon': 'fas fa-chart-pie'
    },
    {
        'endpoint': 'supplier_wallet.transactions',
        'title': 'سجل الحركات المالية',
        'icon': 'fas fa-exchange-alt'
    },
    {
        'endpoint': 'supplier_wallet.withdraw',
        'title': 'طلب سحب الرصيد',
        'icon': 'fas fa-money-bill-wave'
    }
]

def register_module(app):
    # ✅ حماية تسجيل الـ Blueprint لتجنب أي تكرار أو أخطاء
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")

    # ✅ ربط الموديول بالقاموس العام للنظام لكي تظهر القائمة المنسدلة وروابطها فوراً
    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
        
    app.supplier_modules['supplier_wallet'] = {
        'name': MODULE_NAME,
        'icon': MODULE_ICON,
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }
