from flask import Blueprint

# 1. تعريف الـ Blueprint لمركز إدارة محجوب أونلاين
# تم تحديد المجلدات لضمان وصول Flask إلى ملفات HTML و CSS الخاصة بالإدارة
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/admin/static'
)

# 2. ربط المسارات (Routes) بالـ Blueprint
# يتم الاستيراد في نهاية الملف لتجنب خطأ الاستيراد الدائري (Circular Import)
try:
    from . import routes
    print("✅ تم تجهيز مسارات لوحة التحكم بنجاح.")
except Exception as e:
    # طباعة الخطأ في سجلات Railway لتسهيل التتبع إذا وُجد نقص في ملف routes
    print(f"⚠️ فشل استيراد المسارات في admin_panel: {e}")
