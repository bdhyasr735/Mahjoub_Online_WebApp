# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_treasury"
MODULE_NAME = "الرقابة المالية"
DISPLAY_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-wallet"
ICON = "landmark"
VERSION = "2.4.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"
SHOW_IN_ADMIN = True

# ✅ تعريف الروابط والـ Endpoints لتظهر في القائمة الجانبية بسلاسة
LINKS = {
    "admin_treasury.treasury_index": "لوحة الخزينة والقيود المركزية",
    "admin_suppliers_wallets.suppliers_wallets_controller.index": "إدارة محافظ الموردين",
    "admin_suppliers_wallets.suppliers_wallets_controller.withdraw_requests_list": "طلبات السحب"
}

links = LINKS

def get_nav_metadata():
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": [],
        "links": links
    }

def register_module(app):
    """تسجيل موديول الخزينة فقط (محافظ الموردين يُسجل في ملفه الخاص)."""
    try:
        # ✅ تسجيل موديول الخزينة المركزية فقط
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
        else:
            print("ℹ️ [Registry]: موديول 'الخزينة' مُسجل مسبقاً.")
            
        # ❌ تم إزالة تسجيل admin_suppliers_wallets من هنا
        #    ليتم تسجيله فقط من خلال ملفه الخاص (apps/admin_suppliers_wallets/registry.py)
            
    except ImportError as e:
        print(f"❌ [Registry Error]: فشل استيراد الموديول - تأكد من وجود الملفات في المسار الصحيح: {e}")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل الموديولات: {e}")
