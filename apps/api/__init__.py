# coding: utf-8
# 📂 apps/api/__init__.py

from .product_sync_engine import ProductSyncEngine

# إنشاء نسخة من المحرك
engine = ProductSyncEngine()

__all__ = [
    'ProductSyncEngine',
    'engine'
]
