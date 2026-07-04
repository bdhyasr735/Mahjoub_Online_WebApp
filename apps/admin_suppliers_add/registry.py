# coding: utf-8
# 📂 apps/admin_suppliers_add/registry.py

from apps.admin_suppliers_add.routes import admin_suppliers_add_bp

# إعدادات الموديول لتظهر في القائمة الجانبية (Sidebar)
MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-user-plus"

# الروابط التي ستظهر في القائمة المنسدلة
# ملاحظة: تأكد أن اسم الـ Blueprint هو admin_suppliers_add_bp 
# واسم الدالة في routes هو add_supplier_or_staff
LINKS = {
    "إضافة مورد جديد": "admin_suppliers_add_bp.add_supplier_or_staff",
    "قائمة الموردين": "admin_suppliers_add_bp.list_suppliers" # يفضل إضافة هذا الرابط أيضاً للتنقل
}

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بالموديول في تطبيق Flask الرئيسي.
    """
    try:
        # تسجيل الـ Blueprint مع تحديد الـ url_prefix المناسب
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_add': {e}")
