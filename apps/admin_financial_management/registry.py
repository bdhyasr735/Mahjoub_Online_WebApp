# coding: utf-8
# 📂 apps/admin_financial_management/registry.py

from apps.admin_financial_management.routes import financial_bp

MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fa-wallet"

# دمجنا هنا كل الروابط التي تريدها تحت مظلة واحدة
LINKS = {
    "إدارة المحافظ": "financial_bp.manage_wallets",
    "خزينة المنصة": "treasury_bp.dashboard"  # تأكد من اسم الـ Endpoint الصحيح الخاص بالخزينة
}

def register_module(app):
    try:
        app.register_blueprint(financial_bp, url_prefix='/admin/financial')
        print("✅ [Registry]: تم تسجيل موديول 'الرقابة المالية' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: {e}")
