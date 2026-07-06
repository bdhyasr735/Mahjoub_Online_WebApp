# coding: utf-8
from apps.supplier_wallet.routes import supplier_wallet_bp

def register_module(app):
    app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
    print("✅ [Registry] تم تسجيل موديول 'محفظة المورد' بنجاح.")
