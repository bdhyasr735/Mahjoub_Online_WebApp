# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (خزينة المنصة)
في نظام التسجيل المركزي للمشروع
Mahjoub Online WebApp
"""

# ========== بيانات الموديول الأساسية ==========
MODULE_KEY = "admin_treasury"
MODULE_NAME = "الرقابة المالية"
DISPLAY_NAME = "خزينة المنصة"
MODULE_ICON = "fas fa-coins"
ICON = "treasury"
VERSION = "1.0.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"

# يظهر كروابط فرعية تحت الرقابة المالية (وليس في القائمة الرئيسية)
SHOW_IN_ADMIN = False

# ========== روابط القائمة الجانبية ==========
# يجب أن تتطابق أسماء النقاط (Endpoints) مع الـ Blueprint المُسجل في __init__.py و treasury_controller.py
LINKS = {
    "admin_treasury.treasury_index": "سجل حركات الخزينة",
    # يمكنك إضافة مسارات أخرى هنا عند إنشائها، مثل:
    # "admin_treasury.treasury_detail": "تفاصيل السندات"
}

links = LINKS


def get_nav_metadata():
    """إرجاع بيانات الموديول للقائمة الجانبية"""
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": [],
        "links": links,
        "show_in_admin": SHOW_IN_ADMIN
    }


def register_module(app):
    """
    تسجيل موديول خزينة المنصة في التطبيق الرئيسي.
    تُستدعى هذه الدالة من نظام التسجيل المركزي.
    """
    try:
        # استيراد الـ Blueprint الجاهز من ملف __init__.py الخاص بالخزينة
        from apps.admin_treasury import admin_treasury_bp
        
        # ✅ التحقق من عدم تسجيله مسبقاً لتجنب التكرار
        if admin_treasury_bp.name not in app.blueprints:
            app.register_blueprint(admin_treasury_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"   📍 عدد المسارات المسجلة الإضافية للخزينة: {len(admin_treasury_bp.deferred_functions)}")
        else:
            print(f"ℹ️ [Module]: موديول '{MODULE_NAME}' مُسجل مسبقاً (الاسم: {admin_treasury_bp.name})، تم تخطي التسجيل.")
            print(f"   💡 تحقق من عدم وجود تسجيل مزدوج في ملفات registry الأخرى.")
            
    except ImportError as e:
        print(f"❌ [Module Error]: فشل استيراد موديول خزينة المنصة.")
        print(f"   📂 تأكد من وجود ملف __init__.py في المسار: apps/admin_treasury/")
        print(f"   📝 تفاصيل الخطأ: {e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول خزينة المنصة.")
        print(f"   📝 تفاصيل الخطأ: {e}")
