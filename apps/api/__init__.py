# coding: utf-8
# 📂 apps/api/__init__.py

"""
مركز خدمات الـ API.
يتم هنا تجميع الـ Blueprints والمحركات الأساسية لتسهيل الاستيراد.
يضمن هذا الهيكل سهولة الوصول للخدمات وتوحيد حالة المحرك (Singleton).
"""

from .webhooks import webhooks_bp
from .sync_engine import SyncEngine

# إنشاء نسخة واحدة (Singleton) من محرك المزامنة
# يتم استخدامه في كامل التطبيق لتوحيد منطق العمليات وسجلات النظام
engine = SyncEngine()

# تحديد ما يتم تصديره عند الاستيراد، لضمان نظافة مساحة الأسماء
__all__ = [
    'webhooks_bp',
    'SyncEngine',
    'engine'
]
