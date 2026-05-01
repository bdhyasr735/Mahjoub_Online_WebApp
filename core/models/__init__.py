# core/models/__init__.py
# هذا الملف ينظم عملية استيراد الموديلات لضمان رؤيتها من قبل Flask-SQLAlchemy

from core.models.user import User
from core.models.product import Product

# تعريف __all__ يضمن تصدير الكلاسات بشكل صحيح عند استخدام استيراد النجمة
__all__ = ['User', 'Product']
