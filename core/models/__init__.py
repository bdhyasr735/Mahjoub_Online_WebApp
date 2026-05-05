# core/models/__init__.py

# 1. استيراد db من ملف التمديدات المركزي لضمان وحدة الاتصال
from ..extensions import db 

# 2. استيراد الهوية الأساسية (نواة النظام)
from .user import User

# 3. استيراد الموردين (الموديل السيادي الجديد لـ محجوب أونلاين)
# هذا الاستيراد يضمن تسجيل جدول الموردين في قاعدة البيانات فوراً
try:
    from .supplier import Supplier
except ImportError:
    Supplier = None

# 4. استيراد المكونات التجارية (المنتجات والطلبات)
try:
    from .product import Product
except ImportError:
    Product = None

try:
    # الربط مع ملف العمليات التجارية business.py
    from .business import Order
except ImportError:
    Order = None

# 5. تعريف المكونات المتاحة للنظام (الشرعية الرقمية الموحدة)
# أضفنا Supplier هنا ليكون متاحاً عند استدعاء الحزمة
__all__ = ['db', 'User', 'Supplier', 'Product', 'Order']
