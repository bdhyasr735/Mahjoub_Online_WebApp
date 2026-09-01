# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

# ✅ تعريف المتغيرات المطلوبة للاستيراد
MODULE_NAME = "إدارة المالية"
MODULE_ICON = "fas fa-coins"
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
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
    دالة تسجيل موديول المحفظة - يتم استدعاؤها من التطبيق الرئيسي
    """
    try:
        from apps.supplier_wallet.routes import wallet_bp
        
        print("=" * 60)
        print("🔄 [تسجيل موديول]: بدء تسجيل 'supplier_wallet'")
        
        # ✅ 1. تسجيل الـ Blueprint
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(wallet_bp, url_prefix='/supplier/wallet')
            print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")
        
        # ✅ 2. تسجيل الموديول في app.supplier_modules
        if not hasattr(app, 'supplier_modules'):
            app.supplier_modules = {}
        
        # ✅ 3. بناء هيكل الموديول باستخدام المتغيرات المعرفة
        app.supplier_modules['إدارة المالية'] = {
            'name': MODULE_NAME,
            'title': MODULE_NAME,
            'icon': MODULE_ICON,
            'url': '/supplier/wallet/general/transactions',
            'links': LINKS,
            'menu_items': MENU_ITEMS,
            'show_in_supplier': SHOW_IN_SUPPLIER
        }
        
        # ✅ 4. حذف المفتاح القديم إن وجد
        if 'supplier_wallet' in app.supplier_modules:
            del app.supplier_modules['supplier_wallet']
        
        print("🟢 [التسجيل الديناميكي]: ✅ تم تسجيل 'إدارة المالية' مع الروابط:")
        for endpoint, title in LINKS.items():
            print(f"   - {title} ({endpoint})")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ [خطأ التسجيل الديناميكي]: فشل تسجيل موديول 'supplier_wallet'")
        print(f"   السبب: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ✅ تصدير كل المتغيرات والدوال للاستيراد
__all__ = [
    'register_module',
    'LINKS',
    'MENU_ITEMS',
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER'
]
