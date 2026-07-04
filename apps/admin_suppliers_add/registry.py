# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

# احذف السطر التالي من أعلى الملف (السبب الرئيسي للحلقة)
# from .routes import suppliers_bp 

MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-users"

LINKS = {
    "قائمة الشركاء": "suppliers_bp.list_suppliers"
}

def register_module(app):
    # قم بعمل الاستيراد هنا داخل الدالة فقط
    from .routes import suppliers_bp 
    
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_list': {e}")
