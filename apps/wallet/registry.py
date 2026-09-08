# coding: utf-8
# 📂 apps/wallet/registry.py

from apps.wallet.routes import wallet_bp

# ✅ استيراد الملفات الجديدة لضمان تسجيل جميع المسارات (طلبات السحب + سند الصرف)
import apps.wallet.withdrawals
import apps.wallet.receipts

# نترك الاسم والأيقونة للمرجعية البرمجية
MODULE_NAME = "إدارة المحافظ"
MODULE_ICON = "fas fa-wallet"

# ✅ LINKS بشكل قاموس: (Endpoint → Label)
# النظام الديناميكي سيقرأ هذا القاموس ويستخدم safe_url_for() لبناء الرابط تلقائياً
LINKS = {
    'wallet_app.dashboard': 'محافظ الموردين',
    'wallet_app.admin_withdrawals': 'طلبات السحب'
}

def register_module(app):
    """
    تسجيل موديول المحافظ كـ Blueprint مستقل ليتم استدعاؤه برمجياً.
    يتم تسجيل البلوبريت (Blueprint) تلقائياً بنفس المسار المحدد.
    """
    try:
        # تسجيل الـ Blueprint بمسار مستقل
        app.register_blueprint(wallet_bp, url_prefix='/wallet')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المحافظ' بنجاح (وضع الخلفية).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Wallet': {e}")
