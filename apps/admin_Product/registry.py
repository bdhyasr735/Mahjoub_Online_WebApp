# -*- coding: utf-8 -*-
"""
registry.py: تسجيل موديول إدارة المنتجات ديناميكياً في لوحة التحكم المركزية
متجر محجوب أونلاين (www.mahjoub.online)
"""

from .routes import admin_product_bp

# إعدادات العرض في القائمة الجانبية للإدارة
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fa-box-open"
SHOW_IN_SUPPLIER = False  # يظهر للإدارة فقط

# الروابط التي ستظهر تحت هذا الموديول في القائمة الجانبية
LINKS = {
    "قائمة المنتجات": "admin_Product.list_products",
    "إضافة منتج جديد": "admin_Product.create_product"
}

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بالمنتجات مع تحديد مسار البدء /admin/products
    """
    app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
