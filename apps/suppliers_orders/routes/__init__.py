suppliers_product_bp = Blueprint(...)
from . import sync, reviews, stats, products
from .products import register_products_route
register_products_route(suppliers_product_bp)
__all__ = ['suppliers_product_bp']
