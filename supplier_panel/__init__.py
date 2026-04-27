from flask import Blueprint

# 1. تعريف البلوبرنت (Blueprint) الخاص بالموردين
# لاحظ أننا لم نضف url_prefix هنا لأننا قمنا بإضافته في core/__init__.py لضمان المركزية
supplier_bp = Blueprint(
    'supplier_panel', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# 2. ربط المكونات الداخلية (المسارات، المنطق، والحماية)
# الاستيراد يتم في الأسفل لتجنب "الاستيراد الدائري" وضمان تسجيل الروابط بنجاح
try:
    from . import routes 
    from . import auth_logic
    from . import decorators
    
    print("🚀 [System] تم تفعيل بوابة الموردين السيادية بنجاح.")
    
except ImportError as e:
    print(f"⚠️ [Critical Error] فشل في ربط مكونات بوابة الموردين: {e}")

# تصدير الكائن ليكون متاحاً للاستدعاء من ملف core/__init__.py
__all__ = ['supplier_bp']
