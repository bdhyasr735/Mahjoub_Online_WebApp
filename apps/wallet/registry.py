# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# إعدادات الموديول
# أبقينا MODULE_NAME هنا لتعريف الموديول، لكن LINKS فارغ ليتم إخفاؤه من القائمة
MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-wallet"

# ✅ تفريغ الروابط يمنع ظهور هذا الموديول كعنصر مستقل في القائمة الجانبية
LINKS = {}

def register_module(app):
    """
    تسجيل الموديول برمجياً لضمان عمل المسارات داخل التطبيق.
    """
    try:
        # تأكد أن wallet_bp معرف في apps/wallet/routes.py
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'Wallet' بنجاح (مخفي من القائمة).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
