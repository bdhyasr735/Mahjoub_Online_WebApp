# coding: utf-8
# 📂 apps/supplier_wallet/registry.py

from apps.supplier_wallet.routes import supplier_wallet_bp

# 1. إعدادات الموديول للظهور
MODULE_NAME = "محفظة المورد"
MODULE_ICON = "fas fa-wallet"

# 2. هذا المتغير هو الذي يجعله يظهر في قائمة المورد الجانبية (نظام العزل)
SHOW_IN_SUPPLIER = True

# 3. الروابط (تأكد أن اسم الـ blueprint هو 'supplier_wallet' واسم الدالة 'index')
LINKS = {
    "محفظتي": "supplier_wallet.index"
}

def register_module(app):
    """
    تسجيل الموديول في النظام
    """
    try:
        # تسجيل الـ Blueprint الخاص بمحفظة المورد
        app.register_blueprint(supplier_wallet_bp, url_prefix='/supplier/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'محفظة المورد' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'supplier_wallet': {e}")
