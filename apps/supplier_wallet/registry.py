# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

# ============================================
# معلومات الموديول للتسجيل الديناميكي
# ============================================
MODULE_NAME = "supplier_wallet"
DISPLAY_NAME = "الإدارة المالية"
MODULE_ICON = "fa-coins"
SHOW_IN_SUPPLIER = True

# ✅ استخدام مسارات إعادة التوجيه (Redirect)
LINKS = {
    'supplier_wallet.transactions_redirect': 'حركة المحفظة',
    'supplier_wallet.withdraw_redirect': 'سحب الرصيد'
}

# ============================================
# دالة تسجيل الموديول
# ============================================
def register_module(app):
    if wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print(f"✅ [Registry]: تم تسجيل المحفظة المالية بنجاح.")

def init_app(app):
    pass
