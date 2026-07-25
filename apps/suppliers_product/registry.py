# coding: utf-8
# 📂 apps/suppliers_product/registry.py

from flask import Blueprint

# تعريف الـ Blueprint الخاص بالموديول
supplier_product_bp = Blueprint(
    'supplier_product_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/supplier/products'
)

# بيانات التسجيل في الشريط الجانبي
MODULE_NAME = 'إدارة المنتجات'
MODULE_ICON = 'fas fa-box'
SHOW_IN_SUPPLIER = True  # يجب أن تكون True لكي تظهر للموردين

# الروابط التي ستظهر في القائمة الجانبية للموديول
LINKS = {
    'قائمة المنتجات': 'supplier_product_bp.list_products',
    'إضافة منتج جديد': 'add_product_bp.add_product_page', # أو الرابط المناسب داخل الموديول
}

def register_module(app):
    """تسجيل الـ Blueprint في التطبيق الرئيسي"""
    app.register_blueprint(supplier_product_bp)
