# coding: utf-8
# 📂 apps/services/__init__.py

import logging
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
        self._audit = None
    
    @property
    def products(self):
        if self._products is None:
            try:
                from apps.services.product_service import ProductService
                self._products = ProductService(client=self.client)
                logger.info("✅ [Services] تم تحميل ProductService بنجاح")
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل ProductService: {e}")
                self._products = None
        return self._products
    
    @property
    def collections(self):
        if self._collections is None:
            try:
                from apps.services.collection_service import CollectionService
                self._collections = CollectionService(client=self.client)
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل CollectionService: {e}")
                self._collections = None
        return self._collections
    
    @property
    def suppliers(self):
        if self._suppliers is None:
            try:
                from apps.services.supplier_service import SupplierService
                self._suppliers = SupplierService(client=self.client)
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل SupplierService: {e}")
                self._suppliers = None
        return self._suppliers
    
    @property
    def orders(self):
        if self._orders is None:
            try:
                from apps.services.order_service import OrderService
                self._orders = OrderService(client=self.client)
                logger.info("✅ [Services] تم تحميل OrderService بنجاح")
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل OrderService: {e}")
                self._orders = None
        return self._orders
    
    @property
    def users(self):
        if self._users is None:
            try:
                from apps.services.user_service import UserService
                self._users = UserService(client=self.client)
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل UserService: {e}")
                self._users = None
        return self._users

    @property
    def variants(self):
        if self._variants is None:
            try:
                from apps.services.variant_service import VariantService
                self._variants = VariantService(client=self.client)
            except Exception as e:
                logger.error(f"❌ [Services] فشل تحميل VariantService: {e}")
                self._variants = None
        return self._variants

services = Services()