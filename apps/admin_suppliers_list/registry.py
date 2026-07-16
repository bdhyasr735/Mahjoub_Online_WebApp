# 📂 apps/admin_suppliers_list/registry.py

# استيراد البلوبرينتات من ملف الـ routes الخاص بالموديول
# تأكد أن routes.py في هذا المجلد يحتوي على هذه التعريفات
from .routes import suppliers_bp, admin_suppliers_add_bp

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fas fa-users"  # استخدمت أيقونة FontAwesome لتتوافق مع بقية النظام

LINKS = {
    "suppliers_bp.list_suppliers": "قائمة الشركاء",
    "admin_suppliers_add_bp.add_supplier_or_staff": "تعميد شريك جديد"
}

def register_module(app):
    try:
        # تسجيل جميع البلوبرينتات المتعلقة بهذا الموديول
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        
        print("✅ [Registry]: تم تسجيل موديول 'إدارة الموردين' (مع بلوبرينتات الإضافة) بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الموردين: {e}")
