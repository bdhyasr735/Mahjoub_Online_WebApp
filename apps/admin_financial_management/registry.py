# coding: utf-8
# 📂 apps/admin_financial_management/registry.py

# نترك اسم الموديول والأيقونة هنا
MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fa-wallet"

# الروابط صحيحة طالما أن الأسماء تطابق الـ Endpoints في ملفات الـ routes
LINKS = {
    "إدارة المحافظ": "financial_bp.manage_wallets",
    "خزينة المنصة": "treasury_bp.dashboard"
}

def register_module(app):
    """
    تسجيل موديول الرقابة المالية مع استيراد آمن لتجنب تداخل الملفات.
    """
    try:
        # نقوم بالاستيراد هنا فقط عند التشغيل (Lazy Import)
        from apps.admin_financial_management.routes import financial_bp
        
        # تسجيل الـ Blueprint
        app.register_blueprint(financial_bp, url_prefix='/admin/financial')
        
        print("✅ [Registry]: تم تسجيل موديول 'الرقابة المالية' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
