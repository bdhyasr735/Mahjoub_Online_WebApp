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
    # بما أن routes مجلد، يجب أن يحتوي على ملف __init__.py يجمع الـ Blueprint
    # أو نستورده مباشرة من الحزمة
    from apps.supplier_wallet.routes import supplier_wallet_bp
    
    if 'supplier_wallet' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول المحفظة (بنية المجلد) بنجاح.")
