# 📂 apps/admin_suppliers_add/registry.py

# يجب أن يتطابق الاستيراد مع اسم البلوبرينت في routes.py
from apps.admin_suppliers_add.routes import admin_suppliers_add_bp

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-user-plus"

# هذا هو القاموس الذي يربط الرابط بالـ Endpoint الصحيح
LINKS = {
    "إضافة مورد جديد": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    # تسجيل البلوبرينت
    app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers')
    print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
