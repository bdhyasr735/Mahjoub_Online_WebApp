# -*- coding: utf-8 -*-
from .routes import wallet_bp

def register_module(app):
    """تسجيل موديول محفظة المورد في تطبيق Flask الرئيسي"""
    app.register_blueprint(wallet_bp, url_prefix='/supplier')
    
    @app.context_processor
    def inject_supplier_wallet_meta():
        return dict(
            SUPPLIER_WALLET_THEME_COLOR='#4A154B',
            DEFAULT_PER_PAGE=10
        )
