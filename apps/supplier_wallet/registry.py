# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import wallet_bp

supplier_wallet_bp = wallet_bp

MODULE_NAME = "الإدارة المالية"
ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# هيكل الروابط ليتوافق مع القاموس الديناميكي للقائمة الجانبية
LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    """دالة تسجيل الموديول الديناميكي"""
    if 'supplier_wallet' not in app.blueprints and wallet_bp.name not in app.blueprints:
        app.register_blueprint(wallet_bp)
        print("✅ [الإدارة المالية]: تم تسجيل موديول المحفظة بنجاح.")
