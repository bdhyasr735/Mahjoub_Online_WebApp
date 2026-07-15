# 📂 apps/admin_Product/registry.py

from .routes import admin_product_bp

MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"

# التعديل: الترتيب الصحيح هو { "endpoint": "اسم الرابط" }
LINKS = {
    "admin_product.manage_products": "قائمة المنتجات",
    "admin_product.add_product": "إضافة منتج"
}

# إذا كنت تريد ظهور الموديول للمسؤول فقط (وليس للموردين)، تأكد من هذا السطر:
SHOW_IN_SUPPLIER = False 

def register_module(app):
    """
    تسجيل موديول 'إدارة المنتجات' في النظام المركزي.
