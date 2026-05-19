# coding: utf-8
# 🔗 الموثق المركزي لنماذج قاعدة البيانات - محجوب أونلاين 2026
# التوثيق: هذا الملف يجمع كافة الجداول السيادية لضمان تسجيلها في محرك SQLAlchemy

from apps import db

# 1️⃣ استيراد الموديلات (Models) لضمان ربطها بقاعدة البيانات تلقائياً
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import Wallet

# 2️⃣ قائمة الجداول المتاحة للاستيراد السريع والموحد من خارج الحزمة (تمنع خطأ الـ ImportError في الـ Routes)
__all__ = [
    'db',
    'AdminUser',
    'Supplier',
    'Wallet'
]

# 3️⃣ وظائف مساعدة عامة (تستخدم عند الحاجة في الـ Terminal)
def reset_database():
    """وظيفة تستخدم فقط في حالة الطوارئ لإعادة بناء الهيكل الحسابي"""
    db.drop_all()
    db.create_all()
    print("✅ تم إعادة تهيئة قاعدة البيانات السيادية بنجاح.")
