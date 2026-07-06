# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

from apps.suppliers_dashboard.routes import suppliers_dashboard_bp 

# 1. إعدادات الموديول للظهور
MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-tachometer-alt"

# 2. تفعيل الظهور في القائمة الجانبية للمورد
SHOW_IN_SUPPLIER = True

# 3. الروابط: تم توحيدها لتطابق الـ Blueprint في routes.py
LINKS = {
    "الرئيسية": "suppliers_dashboard.dashboard",
    "الإعدادات": "suppliers_dashboard.settings"
}

def register_module(app):
    """
    تسجيل موديول لوحة تحكم المورد في النظام
    """
    try:
        # تسجيل الـ Blueprint باستخدام الاسم الموحد
        # ملاحظة: الروابط معرفة داخل الـ routes بـ /dashboard و /settings
        # لذا سيكون الوصول إليها عبر /supplier/dashboard
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'suppliers_dashboard': {e}")
