from core import db

# 1. استيراد الهوية السيادية من الملف الموحد (user.py)
# تم تغيير المسار هنا ليكون الاستيراد من .user بدلاً من .vendor المحذوف
from .user import User, Vendor, WithdrawRequest

# 2. استيراد المكونات الإضافية مع الحماية من الانهيار
try:
    from .product import Product
except ImportError:
    Product = None

try:
    from .business import Order
except ImportError:
    Order = None

# 3. تعريف المكونات المتاحة للنظام (الترسانة البرمجية)
__all__ = ['db', 'User', 'Vendor', 'WithdrawRequest', 'Product', 'Order']
