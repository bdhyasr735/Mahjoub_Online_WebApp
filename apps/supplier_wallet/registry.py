# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ربط واجهة المحفظة وطلب السحب لتظهر تلقائياً في القائمة الجانبية للموردين
LINKS = {
    'supplier_wallet.withdraw': '💰 المحفظة وطلب السحب'
}

def register_module(app):
    from apps.supplier_wallet.routes import supplier_wallet_bp
    if 'supplier_wallet_bp' not in app.blueprints:
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'supplier_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'supplier_wallet' مسجل مسبقاً.")
