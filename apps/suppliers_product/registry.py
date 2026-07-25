# coding: utf-8
# 📂 apps/suppliers_product/registry.py

from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

# ====== بيانات الموديول للتسجيل التلقائي في السيدبار ======
MODULE_NAME = "إدارة المنتجات"
icon = "fas fa-box-open"

links = {
    "suppliers_product_bp.products": "قائمة المنتجات",
    "add_product_bp.add_product_page": "إضافة منتج جديد"
}


class SupplierProductRegistry:
    """مسجل المكونات والإضافات لمنتجات الموردين"""
    
    def __init__(self):
        self._components = {}

    def register(self, name, component):
        """تسجيل مكون جديد"""
        self._components[name] = component
        logger.info(f"تم تسجيل المكون: {name}")

    def get(self, name):
        """جلب مكون مسجل"""
        return self._components.get(name)

    def list_components(self):
        """عرض جميع المكونات المسجلة"""
        return list(self._components.keys())


# ====== SINGLETON ======
supplier_product_registry = SupplierProductRegistry()


def register_module(app):
    """الدالة التي يبحث عنها مصنع الموديولات لتسجيل الـ Blueprints والمسارات"""
    try:
        # استيراد الـ Blueprints الخاصة بالمنتجات من ملف المسارات
        from apps.suppliers_product.routes import (
            suppliers_product_bp, 
            add_product_bp, 
            edit_product_bp
        )
        
        # تسجيل الـ Blueprints في التطبيق الرئيسي
        app.register_blueprint(suppliers_product_bp)
        app.register_blueprint(add_product_bp)
        app.register_blueprint(edit_product_bp)
        
        logger.info("✅ تم تسجيل موديول 'suppliers_product' بنجاح.")
        return True
    except Exception as e:
        logger.error(f"❌ فشل تسجيل موديول 'suppliers_product': {e}")
        return False
