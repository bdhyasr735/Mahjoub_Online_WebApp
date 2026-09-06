# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py

from apps.supplier_wallet.routes import wallet_bp

def register_module(app):
    """تسجيل موديول المحفظة وتوابعه في التطبيق الرئيسي"""
    app.register_blueprint(wallet_bp)
    return wallet_bp

__all__ = ['wallet_bp', 'register_module']
