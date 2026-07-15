# 📂 apps/admin_suppliers_list/registry.py

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "bi-people-fill" 

# التصحيح: يجب أن يكون الـ endpoint (المسار البرمجي) هو المفتاح (Key)
# والاسم الظاهر هو القيمة (Value)
LINKS = {
    "suppliers_bp.list_suppliers": "قائمة الشركاء",
    "admin_suppliers_add_bp.add_supplier_or_staff": "تعميد شريك جديد"
}

def register_module(app):
    try:
        from .routes import suppliers_bp
        # تأكد من استيراد وتسجيل البلوبرينتات الأخرى إذا كانت مستخدمة
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول الموردين بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الموردين: {e}")
