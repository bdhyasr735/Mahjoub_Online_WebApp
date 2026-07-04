# 📂 apps/admin_suppliers_list/registry.py

MODULE_NAME = "إدارة الشركاء"
MODULE_ICON = "fa-users"

LINKS = {
    "قائمة الشركاء": "suppliers_bp.list_suppliers",
    "تعميد شريك": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    # تسجيل الـ Blueprints هنا
    pass
