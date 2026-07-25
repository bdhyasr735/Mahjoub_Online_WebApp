# coding: utf-8
# 📂 apps/services/__init__.py

from .graphql_client import GraphQLClient
from .product_service import ProductService
from .order_service import OrderService
from .collection_service import CollectionService
from .variant_service import VariantService


class Services:
    """الخدمات الموحدة - تحتوي على جميع خدمات GraphQL"""
    
    def __init__(self):
        self.client = GraphQLClient()
        self.products = ProductService(self.client)
        self.orders = OrderService(self.client)
        self.collections = CollectionService(self.client)
        self.variants = VariantService(self.client)
    
    # ============================================================
    # 🚀 طريقة سريعة للتنفيذ المباشر
    # ============================================================
    
    def execute(self, query: str, variables: dict = None):
        """تنفيذ استعلام GraphQL مباشر"""
        return self.client.execute(query, variables)


# ============================================================
# 🔥 Singleton Instance للاستخدام السريع
# ============================================================

services = Services()
