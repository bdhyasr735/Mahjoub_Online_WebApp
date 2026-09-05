# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

# ============================================
# معلومات الموديول للتسجيل الديناميكي
# ============================================
MODULE_NAME = "supplier_wallet"
DISPLAY_NAME = "إدارة المالية"
MODULE_ICON = "fa-coins"
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

# ============================================
# دالة تسجيل الموديول (مطلوبة للتسجيل الديناميكي)
# ============================================
def register_module(app):
    """تسجيل موديول المحفظة المالية"""
    if wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print(f"✅ [Registry]: تم تسجيل المحفظة المالية بنجاح.")

def init_app(app):
    """تهيئة الموديول (اختياري)"""
    pass
