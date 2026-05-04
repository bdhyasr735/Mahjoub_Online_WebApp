# core/models/__init__.py

from core import db

# 1. استيراد نماذج الهوية والمستخدمين
from core.models.user import User

# 2. استيراد نماذج الأعمال والربط السيادي
# تم تعديل هذا السطر لإزالة الكيانات التي تسببت في الخطأ (Province, District, FinancialEntity)
# لأنها الآن حقول داخل كلاس Supplier وليست كلاسات منفصلة.
from .business import Supplier

# 3. استيراد نماذج المتاجر والمنتجات والطلبات
from .vendor import Vendor
from .product import Product
# تأكد من استيراد Order إذا كان معرفاً داخل business أو vendor
try:
    from .business import Order
except ImportError:
    from .vendor import Order

# استيراد طلبات السحب
try:
    from .vendor import WithdrawRequest
except ImportError:
    WithdrawRequest = None

# 4. تعريف الحزم المصدرة (تحديث القائمة لتطابق الاستيرادات الفعلية)
__all__ = [
    'db',
    'User',
    'Supplier',
    'Order',
    'Vendor',
    'Product',
    'WithdrawRequest'
]
