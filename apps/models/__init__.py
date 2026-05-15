# coding: utf-8
# 🔗 الموثق المركزي لنماذج قاعدة البيانات - محجوب أونلاين 2026
# التوثيق: هذا الملف يجمع كافة الجداول السيادية لضمان تسجيلها في محرك SQLAlchemy

from apps import db

# 1. استيراد الموديلات (Models) لضمان ربطها بقاعدة البيانات
# يتم الاستيراد هنا لكي يتمكن السيرفر من إنشاء الجداول تلقائياً عند استدعاء db.create_all()
try:
    from apps.models.admin_db import AdminUser
    from apps.models.supplier_db import Supplier
    
    # قائمة الجداول المتاحة للاستيراد السريع من خارج الحزمة
    __all__ = ['AdminUser', 'Supplier']
    
except ImportError as e:
    print(f"⚠️ خطأ في استيراد النماذج: تأكد من وجود ملفات admin_db.py و supplier_db.py. التفاصيل: {e}")

# 2. وظائف مساعدة عامة (اختياري)
def reset_database():
    """وظيفة تستخدم فقط في حالة الطوارئ لإعادة بناء الهيكل"""
    db.drop_all()
    db.create_all()
    print("✅ تم إعادة تهيئة قاعدة البيانات السيادية بنجاح.")
