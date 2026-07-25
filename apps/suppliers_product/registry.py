# coding: utf-8
# 📂 apps/suppliers_product/registry.py

"""
مخزن تسجيل موديول إدارة منتجات الموردين
يحتوي على بيانات التعريف والروابط الخاصة بالقائمة الجانبية للنظام.
"""

# تعريف بيانات الموديول والقائمة الجانبية
MODULE_METADATA = {
    "title": "إدارة المنتجات",
    "icon": "fas fa-box-open",
    "links": {
        "suppliers_product_bp.products": "عرض المنتجات",
        "add_product_bp.add_product_page": "إضافة منتج جديد"
    }
}

def register_module(app):
    """
    دالة تسجيل الموديول والبلوبرنتات الخاصة بالمنتجات داخل التطبيق الرئيسي
    """
    from apps.suppliers_product.routes import suppliers_product_bp, add_product_bp, edit_product_bp
    
    app.register_blueprint(suppliers_product_bp)
    app.register_blueprint(add_product_bp)
    app.register_blueprint(edit_product_bp)
