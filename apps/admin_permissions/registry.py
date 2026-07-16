# 📂 apps/admin_permissions/registry.py
from apps.admin_permissions.routes import admin_permissions_bp

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fas fa-user-shield"

# يجب أن يبدأ الـ Key باسم الـ Blueprint المسجل في routes.py
LINKS = {
    "admin_permissions_bp.roles_list": "قائمة الصلاحيات"
}

def register_module(app):
    # تسجيل الـ Blueprint بـ url_prefix متوافق مع المسارات
    app.register_blueprint(admin_permissions_bp, url_prefix='/admin/permissions')
    print("✅ [Registry]: تم تسجيل موديول 'إدارة الصلاحيات' بنجاح.")
