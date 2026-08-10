# -*- coding: utf-8 -*-
"""
registry.py: تسجيل موديول إدارة المنتجات ديناميكياً في لوحة التحكم المركزية
متجر محجوب أونلاين (www.mahjoub.online)
"""

from .routes import admin_product_bp

# إعدادات العرض في القائمة الجانبية للإدارة
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"  # أضفت s لتعمل أيقونات FontAwesome بشكل صحيح
SHOW_IN_SUPPLIER = False  # يظهر للإدارة فقط

# الروابط التي ستظهر تحت هذا الموديول في القائمة الجانبية
# التنسيق هو: {"الاسم_البرمجي_للـ_endpoint": "النص_الذي_يظهر_للمستخدم"}
LINKS = {
    "admin_Product.list_products": "قائمة المنتجات",
    "admin_Product.create_product": "إضافة منتج جديد"
}

def register_module(app):
    """
    تسجيل الـ Blueprint الخاص بالمنتجات مع تحديد مسار البدء /admin/products
    """
    app.register_blueprint(admin_product_bp, url_prefix='/admin/products')

# هذه الدالة اختيارية إذا كان نظامك يقوم بجمع الموديولات تلقائياً عبر استيرادها
def get_module_config():
    return {
        "display_name": MODULE_NAME,
        "icon": MODULE_ICON,
        "links": LINKS,
        "show_in_supplier": SHOW_IN_SUPPLIER
    }
