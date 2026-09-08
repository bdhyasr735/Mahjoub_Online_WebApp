# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# نترك الاسم والأيقونة للمرجعية البرمجية
MODULE_NAME = "إدارة المحافظ"
MODULE_ICON = "fas fa-wallet"

# ✅ إضافة الروابط هنا لضمان ظهور "محافظ الموردين" في القائمة الجانبية تحت الرقابة المالية
LINKS = [
    {
        'title': 'محافظ الموردين',
        'url': '/wallet/admin/dashboard',  # الرابط المباشر
        'icon': 'fas fa-wallet'            # الأيقونة
    }
]

def register_module(app):
    """
    تسجيل موديول المحافظ كـ Blueprint مستقل ليتم استدعاؤه برمجياً،
    مع إظهار الرابط في القائمة الجانبية.
    """
    try:
        # ✅ تصحيح اسم البلوبريت: يجب أن يكون wallet_bp وليس wallet_app
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المحافظ' بنجاح مع إظهار الرابط.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
