# 📂 apps/admin_permissions/registry.py

MODULE_NAME = "إدارة الصلاحيات"
MODULE_ICON = "fas fa-user-shield"

# الروابط التي ستظهر في الشريط الجانبي
LINKS = {
    "قائمة الصلاحيات": "admin_permissions.roles_list",
    "إسناد الصلاحيات": "admin_permissions.assign_permissions"
}

def register_module(app):
    # لا داعي للقيام بـ register_blueprint هنا إذا كان يتم في مكان آخر،
    # يكفي هذا الملف ليقوم "الماسح الضوئي" للنظام بالتعرف على الموديول.
    print("✅ [Registry]: تم تسجيل موديول 'إدارة الصلاحيات' بنجاح.")
