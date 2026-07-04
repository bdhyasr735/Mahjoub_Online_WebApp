# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# تم تحديث الاسم ليظهر بوضوح في القائمة الجانبية
MODULE_NAME = "إدارة المحافظ"
MODULE_ICON = "fas fa-wallet"

# ✅ إضافة الرابط هنا سيجعل الموديول يظهر تلقائياً في القائمة الجانبية
# لاحظ أننا استخدمنا 'wallet_app.dashboard' لأن اسم الـ Blueprint هو 'wallet_app'
LINKS = {
    "محفظة الموردين": "wallet_app.dashboard"
}

def register_module(app):
    """
    تسجيل الموديول برمجياً وتفعيله ليظهر في النظام.
    """
    try:
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المحافظ' وإظهاره في القائمة.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
