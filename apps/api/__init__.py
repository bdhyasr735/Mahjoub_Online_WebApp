# بدلاً من .product_sync_engine
from .sync_engine import ProductSyncEngine 

engine = ProductSyncEngine()

__all__ = [
    'ProductSyncEngine',
    'engine'
]
