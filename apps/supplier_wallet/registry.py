# 📂 apps/supplier_wallet/registry.py
from apps.supplier_wallet.routes import supplier_wallet_bp

def register_supplier_wallet_module(app):
    app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
