# coding: utf-8
# 📂 apps/admin_Product/registry.py

# 1. عنوان الموديول وأيقونته في الشريط الجانبي
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_SUPPLIER = False  # يظهر في لوحة التحكم الإدارية وليس الموردين

# 2. الروابط التابعة للموديول (يجب أن يكون الاسم LINKS حصراً)
LINKS = {
    "admin_product_bp.manage_products": "قائمة المنتجات",
    "admin_product_bp.add_product": "إضافة منتج",
}

# 3. دالة التسجيل التي يستدعيها apps/__init__.py تلقائياً
def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بـ admin_Product داخل تطبيق Flask
    """
    try:
        from apps.admin_Product.routes import admin_product_bp
        app.register_blueprint(admin_product_bp)
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل Blueprint للمنتجات: {e}")
