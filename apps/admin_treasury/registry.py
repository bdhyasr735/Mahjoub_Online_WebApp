# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) وموديول محافظ الموردين
في لوحة الإدارة الرئيسية
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
#    يجب أن يتطابق الاسم مع الـ Blueprint المُسجل فعلياً
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
    """تسجيل موديولات الخزينة ومحافظ الموردين في التطبيق الرئيسي."""
    try:
        # 1. تسجيل موديول الخزينة المركزية (موجود في هذا المجلد)
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
            
        # 2. تسجيل موديول محافظ الموردين (موجود في مجلد منفصل)
        #    نستخدم الدالة التي تُنشئ الـ Blueprint من ملف __init__.py الخاص به
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        suppliers_bp = create_admin_suppliers_wallets_blueprint()
        
        # نتحقق من عدم تسجيله مسبقاً باستخدام اسمه الفريد
        if suppliers_bp.name not in app.blueprints:
            app.register_blueprint(suppliers_bp)
            print("✅ [Registry]: تم تسجيل موديول 'إدارة محافظ الموردين' بنجاح.")
        else:
            print("ℹ️ [Registry]: موديول 'إدارة محافظ الموردين' مُسجل مسبقاً (تم تخطي التسجيل).")
            
    except ImportError as e:
        print(f"❌ [Registry Error]: فشل استيراد الموديول - تأكد من وجود الملفات في المسار الصحيح: {e}")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل الموديولات: {e}")
