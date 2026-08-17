# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية)
في نظام التسجيل المركزي للمشروع
Mahjoub Online WebApp
"""

# ========== بيانات الموديول الأساسية ==========
MODULE_KEY = "admin_treasury"
MODULE_NAME = "الرقابة المالية"
DISPLAY_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-wallet"
ICON = "landmark"
VERSION = "2.4.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"
SHOW_IN_ADMIN = True  # يظهر في القائمة الرئيسية

# ========== روابط القائمة الجانبية ==========
# يجب أن تتطابق أسماء النقاط (Endpoints) مع الـ Blueprint المُسجل
# ملاحظة: روابط محافظ الموردين تشير إلى موديول منفصل
LINKS = {
    "admin_treasury.treasury_index": "لوحة الخزينة والقيود المركزية",
    "admin_suppliers_wallets.suppliers_wallets_controller.index": "إدارة محافظ الموردين",
    "admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list": "طلبات السحب"
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
    تسجيل موديول الخزينة المركزية في التطبيق الرئيسي.
    تُستدعى هذه الدالة من نظام التسجيل المركزي.
    
    ملاحظة: يتم تسجيل موديول محافظ الموردين من خلال ملفه الخاص
            (apps/admin_suppliers_wallets/registry.py) لتجنب التكرار.
    """
    try:
        # ✅ تسجيل موديول الخزينة فقط
        from apps.admin_treasury import admin_treasury_bp
        
        # التحقق من عدم تسجيله مسبقاً
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print(f"✅ [Registry]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"   📍 عدد المسارات الكلي في التطبيق: {len(app.url_map._rules)}")
        else:
            print(f"ℹ️ [Registry]: موديول '{MODULE_NAME}' مُسجل مسبقاً، تم تخطي التسجيل.")
            
        # ❌ تم إزالة تسجيل admin_suppliers_wallets من هنا
        #    ليتم تسجيله فقط من خلال ملفه الخاص
        
    except ImportError as e:
        print(f"❌ [Registry Error]: فشل استيراد موديول الخزينة.")
        print(f"   📂 تأكد من وجود ملف __init__.py في المسار: apps/admin_treasury/")
        print(f"   📝 تفاصيل الخطأ: {e}")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الخزينة.")
        print(f"   📝 تفاصيل الخطأ: {e}")
