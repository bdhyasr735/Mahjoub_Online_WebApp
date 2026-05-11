# admin_panel/__init__.py
from flask import Blueprint
import logging

# 1. إعلان الهوية السيادية لمنطقة الإدارة (The Admin Core)
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates', 
    static_folder='static', 
    url_prefix='/admin' 
)

# 2. بروتوكول الربط السيادي المحدث (Clean Sovereign Linkage)
# تم ترتيب الاستيرادات لضمان عدم حدوث تضارب في الـ Endpoints
try:
    # أ- محرك الحماية والولوج
    from . import auth 
    
    # ب- محرك الرادار والداشبورد الأساسي
    from . import routes 

    # ج- مسار إضافة الموردين (المسار المسبب للـ AssertionError سابقاً)
    # تأكد أن هذا الملف موجود بهذا الاسم بالضبط
    from . import add_supplier_routes

    # د- محرك الخدمات المتقدمة (البحث والفلترة AJAX)
    from . import supplier_service_routes 

    # هـ- محرك حوكمة الطاقم والصلاحيات
    from . import staff_routes

    logging.info("✅ تم تعميد كافة محركات لوحة التحكم بنجاح.")

except ImportError as e:
    logging.error(f"⚠️ تنبيه سيادي: تعذر استدعاء بعض الوحدات: {e}")

"""
--- سجل الاستقرار النهائي (نسخة التوافق v4.8) ---
1. تم إضافة 'add_supplier_routes' لضمان تسجيل دالة الإضافة رسمياً.
2. تم إزالة أي استيرادات دائرية قد تسبب توقف السيرفر في Railway.
3. الالتزام بمبدأ "المصدر الواحد" لتسجيل المسارات لتجنب AssertionError.
"""
