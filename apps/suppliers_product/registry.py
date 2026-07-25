# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
مخزن تسجيل موديول إدارة منتجات الموردين
"""

# المتغيرات التي يبحث عنها محمل النظام في apps/__init__.py
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = True  # ليظهر في قائمة الموردين

LINKS = {
    "suppliers_product_bp.products": "عرض المنتجات",
    "add_product_bp.add_product_page": "إضافة منتج جديد"
}

def register_module(app):
    """
    دالة تسجيل الموديول والبلوبرنتات الخاصة بالمنتجات داخل التطبيق الرئيسي
    """
    from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp
    
    app.register_blueprint(suppliers_product_bp)
    app.register_blueprint(add_product_bp)
    app.register_blueprint(edit_product_bp)
