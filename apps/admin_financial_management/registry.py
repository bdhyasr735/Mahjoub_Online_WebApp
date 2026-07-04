# coding: utf-8
# 📂 apps/admin_financial_management/registry.py

from apps.admin_financial_management.routes import financial_bp

# إعدادات الموديول للظهور في القائمة الجانبية
MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fa-wallet"

# تعريف الروابط المتاحة لهذا الموديول
# تأكد من استبدال 'manage_wallets' باسم الدالة الفعلي في ملف routes.py
LINKS = {
    "إدارة المحافظ": "financial_bp.manage_wallets"
}

def register_module(app):
    """
    دالة تسجيل موديول الإدارة المالية في التطبيق الرئيسي
    """
    try:
        app.register_blueprint(financial_bp, url_prefix='/admin/financial')
        print("✅ [Registry]: تم تسجيل موديول 'Admin Financial Management' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Admin Financial Management': {e}")
