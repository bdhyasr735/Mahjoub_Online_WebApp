# coding: utf-8
from apps.admin_suppliers_add.routes import admin_suppliers_add_bp

# بيانات الموديول
MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-user-plus"

# الربط باستخدام اسم البلوبرينت الموجود في routes.py
# تأكد أن الدالة داخل routes.py تسمى 'add_supplier_or_staff'
LINKS = {
    "إضافة مورد جديد": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    """
    تسجيل الموديول في التطبيق الرئيسي.
    """
    if not app.blueprints.get('admin_suppliers_add_bp'):
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
