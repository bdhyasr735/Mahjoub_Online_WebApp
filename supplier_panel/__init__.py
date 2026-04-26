# --- الترسانة السيادية لشركاء النجاح ---
# الموقع: supplier_panel/__init__.py

from flask import Blueprint

# 1. تعريف البلوبرنت (Blueprint) مع تحديد الموارد الخاصة به
# تم ضبط template_folder ليكون 'templates' ليشير للمجلد الداخلي للموردين
# هذا يضمن استدعاء صفحة login.html الخاصة بالموردين وليس الإدارة
supplier_bp = Blueprint(
    'supplier_panel', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# 2. ربط المسارات والمكونات الحيوية بالبلوبرنت
# ملاحظة سيادية: الاستيراد هنا بعد تعريف supplier_bp هو "مفتاح التشغيل"
# لضمان تسجيل المسارات داخل الكائن دون حدوث استيراد دائم (Circular Import)
try:
    # استيراد ملف المسارات (routes) لكي يتم تسجيل @supplier_bp.route فيه
    from . import routes 
    
    # استيراد المنطق الأمني والتحقق
    from . import auth_logic
    
    # استيراد الملحقات (Decorators) مثل فحص الاعتماد
    from . import decorators
    
    # رسالة نجاح تظهر في سجلات Railway عند الإقلاع للتأكيد الفني
    print("🚀 [System] تم تسجيل مسارات بوابة الموردين بنجاح.")
    
except ImportError as e:
    # في حال وجود
