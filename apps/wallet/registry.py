# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# نترك الاسم والأيقونة للمرجعية البرمجية
MODULE_NAME = "إدارة المحافظ"
MODULE_ICON = "fas fa-wallet"

# ✅ LINKS فارغ لأننا قمنا بنقل روابطه لـ registry الخاص بالرقابة المالية
# هذا يضمن عدم تكرار ظهور الموديول في القائمة الجانبية
LINKS = {}

def register_module(app):
    """
    تسجيل موديول المحافظ كـ Blueprint مستقل ليتم استدعاؤه برمجياً،
    دون أن يتداخل مع ظهور القائمة الجانبية.
    """
    try:
        # تسجيل الـ Blueprint بمسار مستقل ليعمل كخدمة خلفية (Backend Service)
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المحافظ' بنجاح (وضع الخلفية).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
