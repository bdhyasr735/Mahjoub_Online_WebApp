# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

# استيراد الـ Blueprint من ملف routes الخاص بهذا الموديول
from .routes import suppliers_bp

# إعدادات العرض في الشريط الجانبي
MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-users"

# تم حذف "إضافة مورد جديد" من القاموس أدناه
# الآن سيظهر فقط "قائمة الموردين" في الشريط الجانبي
LINKS = {
    "قائمة الموردين": "suppliers_bp.list_suppliers"
}

def register_module(app):
    """
    تسجيل الـ Blueprint في التطبيق
    """
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_list': {e}")
