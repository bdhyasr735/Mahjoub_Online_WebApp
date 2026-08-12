# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/registry.py

"""
سجل موديول محفظة المورد والمدفوعات في منصة محجوب أونلاين
Mahjoub Online - Supplier Wallet Registry
"""

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "bi-wallet2"
SHOW_IN_SUPPLIER = True

LINKS = {
    'wallet.wallet': '💰 كشف الحساب العام',
    'wallet.withdraw': '💸 طلبات السحب'
}

def register_module(app):
    """تسجيل موديول محفظة المورد في تطبيق Flask الرئيسي"""
    from apps.supplier_wallet.routes import wallet_bp
    
    if 'wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")
    
    @app.context_processor
    def inject_supplier_wallet_meta():
        return dict(
            SUPPLIER_WALLET_THEME_COLOR='#4A154B',
            DEFAULT_PER_PAGE=10
        )
