# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from flask import url_for

MODULE_NAME = "محفظة الموردين"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# تعريف القوالب الافتراضية
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
    تسجيل موديول المحفظة كقائمة فرعية تحت إدارة المالية
    """
    from apps.supplier_wallet.routes import wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")

    # التأكد من وجود قاموس الموديولات
    if not hasattr(app, 'supplier_modules'):
        app.supplier_modules = {}
    
    # ✅ تغيير المفتاح ليكون تحت إدارة المالية
    # إذا كان هناك موديول رئيسي اسمه "إدارة المالية"، نضيف المحفظة كقائمة فرعية
    if 'إدارة المالية' not in app.supplier_modules:
        # إذا لم تكن موجودة، ننشئها مع قائمة فرعية
        app.supplier_modules['إدارة المالية'] = {
            'name': 'إدارة المالية',
            'title': 'إدارة المالية',
            'icon': 'fas fa-coins',
            'url': '#',  # لا يوجد رابط رئيسي
            'submenu': []  # قائمة فارغة للقوائم الفرعية
        }
    
    # إضافة المحفظة كقائمة فرعية تحت إدارة المالية
    wallet_submenu = {
        'name': MODULE_NAME,
        'title': MODULE_NAME,
        'icon': MODULE_ICON,
        'url': '/supplier/wallet/general/transactions',  # الصفحة الافتراضية
        'links': LINKS,
        'menu_items': MENU_ITEMS,
        'show_in_supplier': SHOW_IN_SUPPLIER
    }
    
    # إضافة القائمة الفرعية إذا لم تكن موجودة مسبقاً
    if 'submenu' in app.supplier_modules['إدارة المالية']:
        # نتأكد من عدم تكرار الإضافة
        existing = [item for item in app.supplier_modules['إدارة المالية']['submenu'] 
                   if item.get('name') == MODULE_NAME]
        if not existing:
            app.supplier_modules['إدارة المالية']['submenu'].append(wallet_submenu)
    else:
        app.supplier_modules['إدارة المالية']['submenu'] = [wallet_submenu]
    
    print("🟢 [التسجيل الديناميكي]: ✅ تم تسجيل 'محفظة الموردين' كقائمة فرعية تحت 'إدارة المالية'.")
