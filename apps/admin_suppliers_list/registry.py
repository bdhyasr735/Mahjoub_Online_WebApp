# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

# هذه المتغيرات يقرأها النظام تلقائياً لإظهار القائمة
MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-users"

LINKS = {
    "قائمة الشركاء": "suppliers_bp.list_suppliers",
    "تعميد شريك": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    # نضع الاستيراد هنا فقط (Lazy Import) لحل مشكلة الـ Circular Import
    from .routes import suppliers_bp
    
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_list': {e}")
