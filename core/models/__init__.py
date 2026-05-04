from core import db

# استيراد الهوية السيادية فقط
from .user import User
from .vendor import Vendor, WithdrawRequest

# استيراد المنتجات والطلبات (إن وجدت)
try:
    from .product import Product
except ImportError:
    Product = None

try:
    from .business import Order
except ImportError:
    Order = None

__all__ = ['db', 'User', 'Vendor', 'WithdrawRequest', 'Product', 'Order']
