# coding: utf-8
# 📂 apps/api/__init__.py

"""
مركز خدمات الـ API.
يتم هنا تجميع الـ Blueprints والمحركات الأساسية لتسهيل الاستيراد.
"""

# تأكد من أن ملف webhooks.py لا يستورد SyncEngine القديم (قم بتعديله كما ناقشنا سابقاً)
from .webhooks import webhooks_bp
# استيراد المحرك المحدث
from .product_sync_engine import ProductSyncEngine

# إنشاء نسخة واحدة (Singleton) من محرك المزامنة
engine = ProductSyncEngine()

# تحديث ما يتم تصديره
__all__ = [
    'webhooks_bp',
    'ProductSyncEngine',
    'engine'
]
