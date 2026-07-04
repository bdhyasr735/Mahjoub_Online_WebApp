# 📂 apps/admin_suppliers_list/registry.py

from apps.admin_suppliers_list.routes import suppliers_bp

# إعدادات العرض في الشريط الجانبي الديناميكي
MODULE_NAME = "الموردون وشركاء النجاح"
MODULE_ICON = "fas fa-truck"

# الروابط التي ستظهر في القائمة المنسدلة
LINKS = {
    "عرض الكل": "suppliers_bp.list_suppliers",
    "إضافة مورد جديد": "suppliers_bp.add_supplier"
}

def register_module(app):
    """
    تسجيل موديول الموردين (admin_suppliers_list).
    """
    try:
        if suppliers_bp:
            app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
            print(f"✅ [Registry]: تم تسجيل موديول 'admin_suppliers_list' بنجاح على المسار (/suppliers).")
    except Exception as e:
        print(f"❌ [Registry]: فشل تسجيل 'admin_suppliers_list': {e}")
