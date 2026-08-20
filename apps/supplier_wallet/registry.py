# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "bi-wallet2"
SHOW_IN_SUPPLIER = True

# الروابط الخاصة بواجهة المورد فقط
LINKS = {
    'supplier_wallet.wallet_dashboard': '💳 نظرة عامة على المحفظة',
    'supplier_wallet.transactions': '📜 سجل الحركات المالية'
}

def register_module(app):
    # استيراد مسارات المورد حصراً
    from apps.supplier_wallet.wallet_routes import supplier_wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول المحفظة للمورد بنجاح.")
