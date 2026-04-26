# --- الترسانة السيادية لشركاء النجاح ---
# الموقع: supplier_panel/__init__.py

from flask import Blueprint

# 1. تعريف البلوبرنت (Blueprint)
# بما أن القوالب داخل templates/supplier_panel، نترك template_folder='templates'
supplier_bp = Blueprint(
    'supplier_panel', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# 2. ربط المسارات والمكونات الحيوية بالبلوبرنت
# ملاحظة سيادية: يجب التأكد من استيراد routes هنا لضمان تفعيل الروابط
try:
    # نقوم بالاستيراد النسبي لضمان تسجيل @supplier_bp.route
    from . import routes 
    from . import auth_logic
    from . import decorators
    
    print("🚀 [System] تم تسجيل مسارات بوابة الموردين (Supplier Panel) بنجاح.")
    
except ImportError as e:
    print(f"⚠️ [Critical Error] فشل في تحميل مكونات بوابة الموردين: {e}")

# تصدير الكائن ليكون متاحاً لملف core/__init__.py
__all__ = ['supplier_bp']
