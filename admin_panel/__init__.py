from flask import Blueprint

# --- تعريف الـ Blueprint السيادي لمنصة محجوب أونلاين ---
# قمنا بإضافة template_folder لضمان أن Flask يبحث عن login.html داخل المجلد الصحيح
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates',  # تأكيد المسار الداخلي للقوالب
    static_folder='static',        # ربط ملفات CSS/JS الخاصة بلوحة الإدارة
    url_prefix='/admin'            # تأمين المسار تحت بادئة /admin
)

# استيراد المسارات (Routes) بعد تعريف الـ Blueprint لكسر دائرة الاستيراد (Circular Import)
# هذا يضمن أن 'admin_bp' أصبح متاحاً لملف routes.py عند التحميل
try:
    from . import routes
    print("✅ تم تحميل مسارات لوحة التحكم بنجاح")
except ImportError as e:
    print(f"❌ فشل في تحميل المسارات: {str(e)}")
