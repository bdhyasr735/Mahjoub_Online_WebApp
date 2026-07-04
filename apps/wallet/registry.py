# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# تم تغيير الاسم ليكون داخلياً لتجنب التضارب مع موديول "الرقابة المالية"
MODULE_NAME = "Wallet_Internal" 
MODULE_ICON = "fas fa-wallet"

# ✅ تفريغ الروابط يضمن عدم ظهور هذا الموديول كعنصر مستقل في القائمة الجانبية
LINKS = {}

def register_module(app):
    """
    تسجيل الموديول برمجياً لضمان عمل المسارات (/wallet/...) داخل التطبيق
    دون إظهاره كعنصر قائمة منفصل.
    """
    try:
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'Wallet' بنجاح (مخفي من القائمة).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
