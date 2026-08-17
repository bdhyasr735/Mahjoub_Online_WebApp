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

# ✅ تم التعديل هنا: تم تغيير False إلى True لتظهر في القائمة الجانبية
SHOW_IN_ADMIN = True

# ========== روابط القائمة الجانبية ==========
LINKS = {
    "admin_treasury.treasury_index": "سجل حركات الخزينة",
}

links = LINKS


def get_nav_metadata():
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
    try:
        from apps.admin_treasury import admin_treasury_bp
        if admin_treasury_bp.name not in app.blueprints:
            app.register_blueprint(admin_treasury_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"   📍 عدد المسارات المسجلة الإضافية للخزينة: {len(admin_treasury_bp.deferred_functions)}")
        else:
            print(f"ℹ️ [Module]: موديول '{MODULE_NAME}' مُسجل مسبقاً.")
    except ImportError as e:
        print(f"❌ [Module Error]: فشل استيراد موديول خزينة المنصة. تفاصيل: {e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول خزينة المنصة. تفاصيل: {e}")
