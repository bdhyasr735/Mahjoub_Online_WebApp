# -*- coding: utf-8 -*-
"""
registry.py: سجل وحدة موديول admin_Product لمنصة متجر محجوب أونلاين
(www.mahjoub.online)
"""

from . import admin_product_bp

MODULE_META = {
    'id': 'admin_Product',
    'name': 'إدارة المنتجات المتطورة',
    'version': '1.0.0',
    'description': 'وحدة إدارة كافة المنتجات، الأقسام، خيارات متعدد الصور، والـ SEO لمتجر محجوب أونلاين',
    'author': 'Mahjoub Online Team',
    'blueprint': admin_product_bp,
    'url_prefix': '/admin/products',
    'icon': 'box-seam',
    'order': 10,
    'permissions': ['view_products', 'manage_products', 'create_products']
}

def register_module(app):
    """
    تسجيل موديول admin_Product في تطبيق الـ Flask الرئيسي
    """
    if 'admin_Product' not in app.blueprints:
        app.register_blueprint(admin_product_bp, url_prefix=MODULE_META['url_prefix'])
    return True

def get_menu_items():
    """
    عناصر القائمة الجانبية (Sidebar) لوحة التحكم Admin Navigation
    """
    return [
        {
            'title': 'المنتجات',
            'endpoint': 'admin_Product.list_products',
            'icon': 'box-seam',
            'order': 10,
            'children': [
                {'title': 'جميع المنتجات', 'endpoint': 'admin_Product.list_products'},
                {'title': 'إضافة منتج جديد', 'endpoint': 'admin_Product.create_product'},
            ]
        }
    ]
