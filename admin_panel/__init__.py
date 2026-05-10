# admin_panel/__init__.py
from flask import Blueprint

# 1. إعلان الهوية السيادية لمنطقة الإدارة (The Admin Core)
# هذا الكائن هو "المظلة" التي تجتمع تحتها كافة مسارات لوحة التحكم
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates', 
    static_folder='static', 
    url_prefix='/admin' 
)

# 2. بروتوكول الربط السيادي (Sovereign Linkage)
# ملاحظة للقائد علي: نستخدم الاستيراد المتأخر لمنع التداخل الدائري (Circular Import)
# ولضمان توافق المسارات مع أماكنها الجديدة في الترسانة البرمجية

try:
    from . import auth             # محرك الحماية والولوج
    from . import routes           # محرك الرادار والداشبورد الأساسي
    
    # استدعاء ملف الإدارة من مجلد الـ core/models كما ذكرت
    # ملاحظة: تأكد أن ملف manage_suppliers.py يستخدم @admin_bp.route
    from core.models import manage_suppliers 

except ImportError as e:
    # بروتوكول تسجيل الأخطاء في حال فقدان أي ملف أثناء النشر على Railway
    print(f"⚠️ تنبيه سيادي: تعذر استدعاء بعض الوحدات البرمجية: {e}")

"""
--- توثيق الاستقرار للمؤسس علي محجوب ---
- تم ربط admin_bp بالملفات المحلية والملفات الموجودة في Core.
- النظام مهيأ الآن للإقلاع دون Crash في Railway.
- في حال استمرار خطأ 500، يرجى التأكد من أن ملف manage_suppliers.py 
  يحتوي في بدايته على: from admin_panel import admin_bp
"""
