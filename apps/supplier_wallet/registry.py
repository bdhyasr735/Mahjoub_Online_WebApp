# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "الإدارة المالية"
MODULE_ICON = "bi-wallet2"
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.wallet_dashboard': '💳 نظرة عامة على المحفظة',
    'supplier_wallet.transactions': '📜 سجل الحركات المالية'
}

def register_module(app):
    # نقوم بالاستيراد مباشرة من ملف wallet_routes الموجود عندك في المجلد
    from apps.supplier_wallet.wallet_routes import supplier_wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")
