# apps/suppliers_product/registry.py

"""
مخزن تسجيل موديول إدارة منتجات الموردين
يحتوي على بيانات التعريف والروابط الخاصة بالقائمة الجانبية للنظام.
"""

# تعريف بيانات الموديول
MODULE_METADATA = {
    "title": "إدارة المنتجات",
    "icon": "fas fa-box-open",
    "links": {
        "suppliers_product.list_products": "عرض المنتجات",
        "suppliers_product.add_product": "إضافة منتج جديد"
    }
}

def register_module(app):
    """
    دالة تسجيل الموديول وبلوبرنت المنتجات داخل التطبيق الرئيسي
    """
    from .routes import suppliers_product_bp
    app.register_blueprint(suppliers_product_bp)
