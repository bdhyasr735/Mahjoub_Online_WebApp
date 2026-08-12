from flask import Blueprint

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    url_prefix='/supplier',
    template_folder='templates',
    static_folder='static'
)

def register_module(app):
    """تسجيل موديول محفظة المورد في تطبيق Flask الرئيسي"""
    from .routes import wallet_bp
    app.register_blueprint(supplier_wallet_bp)
    
    @app.context_processor
    def inject_supplier_wallet_meta():
        return dict(
            SUPPLIER_WALLET_THEME_COLOR='#4A154B',
            DEFAULT_PER_PAGE=10
        )
