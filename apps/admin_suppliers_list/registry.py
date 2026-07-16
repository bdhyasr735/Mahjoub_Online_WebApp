# 📂 apps/admin_suppliers_list/registry.py

# استورد فقط ما هو موجود فعلياً في ملف routes.py
from .routes import suppliers_bp 

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fas fa-users"

LINKS = {
    "suppliers_bp.list_suppliers": "قائمة الشركاء",
    "suppliers_bp.add_supplier_or_staff": "تعميد شريك جديد" # تأكد أن الدالة موجودة بهذا الاسم في routes.py
}

def register_module(app):
    try:
        # تسجيل بلوبرينت واحد فقط
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول الموردين بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الموردين: {e}")
