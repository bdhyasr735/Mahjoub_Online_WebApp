# coding: utf-8
# 📂 apps/admin_suppliers_list/registry.py

from .routes import suppliers_bp

MODULE_NAME = "قائمة الشركاء"
MODULE_ICON = "fa-users"

# ✅ الربط تحت المظلة الرئيسية "إدارة الموردين"
# النظام سيكتشف وجود نفس المفتاح ("إدارة الموردين") في الموديولين وسيدمجهما تلقائياً
LINKS = {
    "إدارة الموردين": {
        "قائمة الشركاء": "suppliers.list_suppliers" # تأكد من اسم الـ Route هنا
    }
}

def register_module(app):
    try:
        app.register_blueprint(suppliers_bp, url_prefix='/admin/suppliers')
        print("✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'admin_suppliers_list': {e}")
