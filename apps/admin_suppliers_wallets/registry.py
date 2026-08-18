# -*- coding: utf-8 -*-
# 📂 apps/admin_suppliers_wallets/registry.py

MODULE_KEY = "admin_suppliers_wallets"
MODULE_NAME = "إدارة محافظ الموردين"
DISPLAY_NAME = "محافظ الموردين"
MODULE_ICON = "fas fa-wallet"
ICON = "wallet"
VERSION = "2.4.0"
URL_PREFIX = "/admin/suppliers-wallets"
REQUIRED_PERMISSION = "manage_platform_treasury"
SHOW_IN_ADMIN = True  # ✅ تم تفعيله ليظهر في القائمة الجانبية السيادية

# ✅ تحديث الروابط لتطابق أسماء الـ Blueprints المستقلة الجديدة
LINKS = {
    "wallets_controller.index": "عرض المحافظ",
    "withdraw_requests_controller.withdraw_requests_list": "طلبات السحب"
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
        from apps.admin_suppliers_wallets import create_admin_suppliers_wallets_blueprint
        wallets_bp = create_admin_suppliers_wallets_blueprint()
        
        if wallets_bp.name not in app.blueprints:
            app.register_blueprint(wallets_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"    📍 عدد المسارات المسجلة: {len(app.url_map._rules)}")
        else:
            print(f"ℹ️ [Module]: موديول '{MODULE_NAME}' مُسجل مسبقاً (الاسم: {wallets_bp.name})، تم تخطي التسجيل.")
            
    except ImportError as e:
        print(f"❌ [Module Error]: فشل استيراد موديول محافظ الموردين. تفاصيل: {e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول محافظ الموردين. تفاصيل: {e}")
