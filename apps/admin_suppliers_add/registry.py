# coding: utf-8
# 📂 apps/admin_suppliers_add/registry.py

# هذه المتغيرات ضرورية ليقوم __init__.py باكتشاف الموديول وربط الروابط
MODULE_NAME = "إدارة الموردين"
MODULE_ICON = "fa-user-plus"
LINKS = {
    "تعميد مورد جديد": "admin_suppliers_add_bp.add_supplier_or_staff"
}

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بموديول إضافة الموردين.
    """
    try:
        from .routes import admin_suppliers_add_bp
        
        app.register_blueprint(admin_suppliers_add_bp, url_prefix='/admin/suppliers_add')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح (خلفية).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_add': {e}")
