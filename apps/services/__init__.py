# coding: utf-8
# 📂 apps/services/__init__.py

"""
خدمات التطبيق - واجهة موحدة للوصول إلى جميع الخدمات
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================
# 🔧 تحميل الخدمات (Lazy Loading)
# ============================================

class Services:
    """
    واجهة موحدة للوصول إلى جميع خدمات التطبيق
    استخدام Lazy Loading لتجنب circular import
    """
    
    def __init__(self):
        self._products = None
        self._collections = None
        self._suppliers = None
        self._orders = None
        self._users = None
        self._variants = None
    
    @property
    def products(self):
        """خدمة المنتجات"""
        if self._products is None:
            try:
                from apps.services.product_service import ProductService
                self._products = ProductService()
            except ImportError as e:
                logger.warning(f"⚠️ ProductService غير متوفرة: {e}")
                self._products = None
        return self._products
    
    @property
    def collections(self):
        """خدمة المجموعات"""
        if self._collections is None:
            try:
                from apps.services.collection_service import CollectionService
                self._collections = CollectionService()
            except ImportError as e:
                logger.warning(f"⚠️ CollectionService غير متوفرة: {e}")
                self._collections = None
        return self._collections
    
    @property
    def suppliers(self):
        """خدمة الموردين"""
        if self._suppliers is None:
            try:
                from apps.services.supplier_service import SupplierService
                self._suppliers = SupplierService()
            except ImportError as e:
                logger.warning(f"⚠️ SupplierService غير متوفرة: {e}")
                self._suppliers = None
        return self._suppliers
    
    @property
    def orders(self):
        """خدمة الطلبات"""
        if self._orders is None:
            try:
                from apps.services.order_service import OrderService
                self._orders = OrderService()
            except ImportError as e:
                logger.warning(f"⚠️ OrderService غير متوفرة: {e}")
                self._orders = None
        return self._orders
    
    @property
    def users(self):
        """خدمة المستخدمين"""
        if self._users is None:
            try:
                from apps.services.user_service import UserService
                self._users = UserService()
            except ImportError as e:
                logger.warning(f"⚠️ UserService غير متوفرة: {e}")
                self._users = None
        return self._users
    
    @property
    def variants(self):
        """خدمة المتغيرات"""
        if self._variants is None:
            try:
                from apps.services.variant_service import VariantService
                self._variants = VariantService()
            except ImportError as e:
                logger.warning(f"⚠️ VariantService غير متوفرة: {e}")
                self._variants = None
        return self._variants


# ✅ إنشاء كائن واحد للاستخدام العام
services = Services()


# ============================================
# 🚀 دوال مساعدة للوصول السريع
# ============================================

def get_products():
    """الحصول على خدمة المنتجات"""
    return services.products


def get_collections():
    """الحصول على خدمة المجموعات"""
    return services.collections


def get_suppliers():
    """الحصول على خدمة الموردين"""
    return services.suppliers


def get_orders():
    """الحصول على خدمة الطلبات"""
    return services.orders


def get_users():
    """الحصول على خدمة المستخدمين"""
    return services.users


def get_variants():
    """الحصول على خدمة المتغيرات"""
    return services.variants


# ============================================
# 📦 الاستخدام
# ============================================

# ✅ الآن يمكنك استخدامها بهذه الطريقة:
# from apps.services import services
# 
# all_products = services.products.get_all()
# all_collections = services.collections.get_all()
# 
# # أو
# from apps.services import get_products
# products = get_products().get_all()


__all__ = [
    'services',
    'get_products',
    'get_collections',
    'get_suppliers',
    'get_orders',
    'get_users',
    'get_variants'
]
