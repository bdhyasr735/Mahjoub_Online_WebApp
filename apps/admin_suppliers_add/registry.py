# coding: utf-8
# 📂 apps/admin_suppliers_add/registry.py

from apps.admin_suppliers_add.routes import admin_suppliers_add_bp

MODULE_NAME = "إضافة شريك"
MODULE_ICON = "fa-user-plus"

# ✅ الربط تحت المظلة الرئيسية "إدارة الموردين"
LINKS = {
    "إدارة الموردين": {
        "إضافة شريك": "admin_suppliers_add.add_supplier" # تأكد من اسم الـ Route هنا
    }
}

def register_module(app):
    try:
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers/add')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_add': {e}")
