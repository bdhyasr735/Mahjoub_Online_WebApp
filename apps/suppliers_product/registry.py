# coding: utf-8
# 📂 apps/suppliers_product/registry.py

import logging

logger = logging.getLogger(__name__)


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
