# coding: utf-8
# 📂 apps/services/__init__.py

import logging
from typing import Optional
from apps.services.graphql_client import GraphQLClient

logger = logging.getLogger(__name__)

class Services:
    def __init__(self):
        # إنشاء عميل GraphQL موحد للخدمات
        self.client = GraphQLClient()
        
        self._products = None
        self._collections = None
        self._suppliers = None
        self._orders = None
        self._users = None
        self._variants = None
    
    @property
    def products(self):
        if self._products is None:
            try:
                from apps.services.product_service import ProductService
                self._products = ProductService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ ProductService غير متوفرة: {e}")
                self._products = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل ProductService: {e}")
                self._products = None
        return self._products
    
    @property
    def collections(self):
        if self._collections is None:
            try:
                from apps.services.collection_service import CollectionService
                self._collections = CollectionService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ CollectionService غير متوفرة: {e}")
                self._collections = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل CollectionService: {e}")
                self._collections = None
        return self._collections
    
    @property
    def suppliers(self):
        if self._suppliers is None:
            try:
                from apps.services.supplier_service import SupplierService
                self._suppliers = SupplierService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ SupplierService غير متوفرة: {e}")
                self._suppliers = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل SupplierService: {e}")
                self._suppliers = None
        return self._suppliers
    
    @property
    def orders(self):
        if self._orders is None:
            try:
                from apps.services.order_service import OrderService
                self._orders = OrderService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ OrderService غير متوفرة: {e}")
                self._orders = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل OrderService: {e}")
                self._orders = None
        return self._orders
    
    @property
    def users(self):
        if self._users is None:
            try:
                from apps.services.user_service import UserService
                self._users = UserService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ UserService غير متوفرة: {e}")
                self._users = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل UserService: {e}")
                self._users = None
        return self._users
    
    @property
    def variants(self):
        if self._variants is None:
            try:
                from apps.services.variant_service import VariantService
                self._variants = VariantService(client=self.client)
            except ImportError as e:
                logger.warning(f"⚠️ VariantService غير متوفرة: {e}")
                self._variants = None
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل VariantService: {e}")
                self._variants = None
        return self._variants

services = Services()

def get_products(): return services.products
def get_collections(): return services.collections
def get_suppliers(): return services.suppliers
def get_orders(): return services.orders
def get_users(): return services.users
def get_variants(): return services.variants

__all__ = [
    'services',
    'get_products',
    'get_collections',
    'get_suppliers',
    'get_orders',
    'get_users',
    'get_variants'
]
