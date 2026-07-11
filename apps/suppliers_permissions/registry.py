# 📂 apps/suppliers_permissions/registry.py

from apps.suppliers_permissions.routes import suppliers_permissions_bp

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fas fa-users-cog" # تأكد من إضافة fas لتعمل الأيقونة

# الصيغة الصحيحة: { 'endpoint_name': 'الاسم الذي سيظهر للمستخدم' }
LINKS = {
    "suppliers_permissions.permissions": "صلاحيات الموظفين"
}

SHOW_IN_SUPPLIER = True

def register_module(app):
    app.register_blueprint(suppliers_permissions_bp, url_prefix='/supplier')
