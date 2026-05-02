# core/models/__init__.py

# استيراد كائن db من الحزمة المركزية لضمان استخدام نفس المحرك
from core import db

# استيراد الموديلات بشكل مباشر ليتم التعرف عليها عند تشغيل db.create_all()
from core.models.user import User

# ملاحظة: بمجرد إنشاء ملفات الموردين والطلبات، قم بإلغاء التعليق عن الأسطر التالية:
# from core.models.supplier import Supplier
# from core.models.order import Order

# تجميع الموديلات في قائمة واحدة لتسهيل العمليات البرمجية إذا لزم الأمر
__all__ = [
    'User',
    # 'Supplier',
    # 'Order'
]
