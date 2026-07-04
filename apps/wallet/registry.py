# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# تم تحديث الاسم ليكون مناسباً للواجهة
MODULE_NAME = "إدارة المحافظ" 
MODULE_ICON = "fas fa-wallet"

# ✅ إضافة الروابط هنا سيجعلها تظهر تلقائياً في القائمة الجانبية بفضل نظام الـ Auto-Discovery
# تأكد أن 'wallet_bp.dashboard' هو اسم الدالة (route) الصحيح في ملف routes.py الخاص بك
LINKS = {
    "محفظة الموردين": "wallet_bp.dashboard"
}

def register_module(app):
    """
    تسجيل الموديول برمجياً وتفعيله في القائمة الجانبية.
    """
    try:
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'Wallet' وإظهاره في القائمة.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
