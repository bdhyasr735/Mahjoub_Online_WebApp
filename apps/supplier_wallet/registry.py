# coding: utf-8
# 📂 apps/suppliers_wallet/registry.py

MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fas fa-wallet"
SHOW_IN_SUPPLIER = True

# ✅ الـ Endpoint الخاص بلوحة محفظة المورد
LINKS = {
    'suppliers_wallet_bp.supplier_wallet_view': '💰 إدارة المحفظة'
}

def register_module(app):
    from apps.suppliers_wallet.routes import suppliers_wallet_bp
    # ✅ حماية إضافية: التحقق من عدم التسجيل المسبق لتجنب أي أخطاء في الـ Blueprint
    if 'suppliers_wallet_bp' not in app.blueprints:
        app.register_blueprint(suppliers_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_wallet' بنجاح.")
    else:
        print("ℹ️ [Registry]: موديول 'suppliers_wallet' مسجل مسبقاً.")
