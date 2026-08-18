# -*- coding: utf-8 -*-
# 📂 apps/admin_suppliers_wallets/registry.py
"""
تسجيل موديول إدارة محافظ الموردين وطلبات السحب
في نظام التسجيل المركزي للمشروع
Mahjoub Online WebApp
"""

# ========== بيانات الموديول الأساسية ==========
MODULE_KEY = "admin_suppliers_wallets"
MODULE_NAME = "إدارة محافظ الموردين"
DISPLAY_NAME = "محافظ الموردين"
MODULE_ICON = "fas fa-wallet"
ICON = "wallet"
VERSION = "2.4.0"
URL_PREFIX = "/admin/suppliers-wallets"
REQUIRED_PERMISSION = "manage_platform_treasury"

# يظهر كروابط فرعية تحت الرقابة المالية (وليس في القائمة الرئيسية)
SHOW_IN_ADMIN = False

# ========== روابط القائمة الجانبية ==========
# ✅ تم تحديث الاسم ليتوافق مع التعديل في ملف الـ Controller (wallets_controller)
LINKS = {
    "admin_suppliers_wallets.wallets_controller.index": "عرض المحافظ",
    "admin_suppliers_wallets.wallets_controller.withdraw_requests_list": "طلبات السحب"
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
    تسجيل موديول محافظ الموردين في التطبيق الرئيسي.
    تُستدعى هذه الدالة من نظام التسجيل المركزي.
    """
    try:
        # استيراد دالة إنشاء الـ Blueprint من ملف __init__.py
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        
        # ✅ التحقق من عدم تسجيله مسبقاً لتجنب التكرار
        if wallets_bp.name not in app.blueprints:
            app.register_blueprint(wallets_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"   📍 عدد المسارات المسجلة: {len(app.url_map._rules)}")
        else:
            print(f"ℹ️ [Module]: موديول '{MODULE_NAME}' مُسجل مسبقاً (الاسم: {wallets_bp.name})، تم تخطي التسجيل.")
            print(f"   💡 تحقق من عدم وجود تسجيل مزدوج في ملفات registry الأخرى.")
            
    except ImportError as e:
        print(f"❌ [Module Error]: فشل استيراد موديول محافظ الموردين.")
        print(f"   📂 تأكد من وجود ملف __init__.py في المسار: apps/admin_suppliers_wallets/")
        print(f"   📝 تفاصيل الخطأ: {e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول محافظ الموردين.")
        print(f"   📝 تفاصيل الخطأ: {e}")