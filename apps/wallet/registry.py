# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# نترك الاسم والأيقونة كما هما لتعريف الموديول برمجياً
MODULE_NAME = "إدارة المحافظ"
MODULE_ICON = "fas fa-wallet"

# ✅ نجعل القائمة فارغة هنا، لأننا قمنا بتعريفها بالفعل داخل 'الرقابة المالية'
# هذا يمنع ظهورها كعنصر مستقل في القائمة الجانبية ويجعلها تعمل في الخلفية فقط
LINKS = {}

def register_module(app):
    """
    تسجيل الموديول برمجياً وتفعيله ليظهر في النظام.
    """
    try:
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المحافظ' بنجاح (مدمج في الرقابة المالية).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
