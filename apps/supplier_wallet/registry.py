# 📂 apps/supplier_wallet/registry.py

SHOW_IN_SUPPLIER = True  # 👈 هذا هو مفتاح ظهور الموديول في لوحة الموردين
MODULE_NAME = "المحفظة المالية"
ICON = "fa-wallet"

# وباقي تعريف القوائم...
NAV_ITEMS = [
    {"endpoint": "supplier_wallet.wallet_dashboard", "title": "رئيسية المحفظة"},
    {"endpoint": "supplier_wallet.transactions_list", "title": "سجل المعاملات"}
]

def register_module(app):
    # تسجيل الـ Blueprint الخاص بالمحفظة هنا
    from apps.supplier_wallet.routes import supplier_wallet_bp
    app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
