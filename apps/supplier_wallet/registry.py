# apps/supplier_wallet/registry.py

from flask import url_for

MODULE_NAME = "إدارة المالية"
MODULE_ICON = "fas fa-coins"
SHOW_IN_SUPPLIER = True

LINKS = {
    'supplier_wallet.transactions': 'حركة المحفظة',
    'supplier_wallet.withdraw': 'سحب الرصيد'
}

def register_module(app):
    try:
        from apps.supplier_wallet.routes import supplier_wallet_bp
        
        if 'supplier_wallet' not in app.blueprints:
            app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
            print("✅ [Registry]: تم تسجيل بلوبرنت 'supplier_wallet' بنجاح.")
            
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
