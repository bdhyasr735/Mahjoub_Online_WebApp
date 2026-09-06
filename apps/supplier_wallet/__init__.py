# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/__init__.py

from apps.supplier_wallet.routes import supplier_wallet_bp

def init_app(app):
    """تسجيل بلوبرنت محفظة المورد في التطبيق الرئيسي"""
    app.register_blueprint(supplier_wallet_bp)
