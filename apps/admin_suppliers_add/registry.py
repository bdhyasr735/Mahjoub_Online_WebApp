# 📂 apps/admin_suppliers_add/registry.py

# 1. استيراد البلوبرينت المعرف في ملف المسارات
from apps.admin_suppliers_add.routes import suppliers_bp

# 2. تعريف بيانات الموديول (هذه المتغيرات يقرؤها المحرك التلقائي في __init__.py)
MODULE_NAME = "إضافة موردين"
MODULE_ICON = "fa-user-plus"
LINKS = {
    "إضافة مورد جديد": "admin_suppliers_add.add_supplier_route" 
    # ملاحظة: تأكد أن "admin_suppliers_add.add_supplier_route" يطابق اسم الـ endpoint في routes.py
}

def register_module(app):
    """
    تسجيل موديول إضافة الموردين.
    """
    # تسجيل البلوبرينت
    app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
    
    print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_add' بنجاح.")
