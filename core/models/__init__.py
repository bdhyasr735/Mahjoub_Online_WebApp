# core/models/__init__.py

# 1. استيراد قاعدة البيانات (db) لضمان وحدة الاتصال عبر كافة الموديلات
from core.extensions import db 

# 2. استيراد الهوية الأساسية (النواة الرقمية للنظام)
from .user import User

# 3. استيراد الموردين (الموديل السيادي المطور لـ محجوب أونلاين)
# تسجيل هذا الموديل هنا يضمن تفعيل المحفظة متعددة العملات (Multi-Currency Vault)
try:
    from .supplier import Supplier
except ImportError:
    # في حال لم يتم العثور على الملف، يتم تعريفه كـ None لتجنب انهيار السيرفر
    Supplier = None
    print("⚠️ Warning: Supplier model not found in core/models")

# 4. استيراد المكونات التجارية (المنتجات والعمليات)
try:
    from .product import Product
except ImportError:
    Product = None

try:
    # الربط مع سجل العمليات التجارية (الطلبات)
    from .business import Order
except ImportError:
    Order = None

# 5. بروتوكول التصدير الموحد (__all__)
# هذا البروتوكول يسمح باستدعاء الموديلات بسهولة عبر: from core.models import Supplier
__all__ = [
    'db', 
    'User', 
    'Supplier', 
    'Product', 
    'Order'
]

# رسالة تأكيد في سجلات السيرفر عند اكتمال بناء الترسانة
# print("✅ Sovereign Models Registry: Initialized Successfully.")
