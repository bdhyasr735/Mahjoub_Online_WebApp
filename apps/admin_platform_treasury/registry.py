# coding: utf-8
# 📂 apps/admin_platform_treasury/registry.py

from apps.admin_platform_treasury.routes import platform_treasury_bp # تأكد من اسم الـ Blueprint الصحيح

# يمكنك إبقاء الاسم كما هو أو تغييره
MODULE_NAME = "الخزينة" 
MODULE_ICON = "fa-money-bill"

# ✅ التعديل الجوهري: تفريغ الروابط سيمنع هذا الموديول من الظهور كعنصر مستقل في الشريط الجانبي
LINKS = {} 

def register_module(app):
    """
    تسجيل الـ Blueprint لضمان عمل المسارات برمجياً، 
    دون إظهاره كعنصر مكرر في القائمة الجانبية.
    """
    try:
        app.register_blueprint(platform_treasury_bp, url_prefix='/admin/treasury')
        print("✅ [Registry]: تم تسجيل موديول 'Admin Platform Treasury' بنجاح (مخفي من القائمة).")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'Admin Platform Treasury': {e}")
