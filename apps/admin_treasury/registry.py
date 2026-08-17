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

# ✅ الروابط الرئيسية للموديول
links = {
    "admin_treasury.treasury_index": "لوحة الخزينة والقيود المركزية"
}

# ✅ التنقل والشريط الجانبي (تم تصحيح الـ Endpoints)
NAV_ITEMS = [
    {
        "id": "treasury_overview",
        "title": "لوحة الخزينة المركزية",
        "endpoint": "admin_treasury.treasury_index",
        "icon": "chart-pie",
        "permission": "view_treasury"
    },
    {
        "id": "suppliers_wallets_management",
        "title": "إدارة محافظ الموردين",
        "endpoint": "admin_suppliers_wallets.index",  # ✅ صحيح
        "icon": "wallet",
        "permission": "view_suppliers_wallets"
    },
    {
        "id": "suppliers_withdraw_requests",
        "title": "طلبات السحب",
        "endpoint": "admin_suppliers_wallets.withdraw_requests_list",  # ✅ تم إصلاح الخطأ هنا
        "icon": "money-bill-transfer",
        "permission": "manage_withdraw_requests"
    }
]

# للحفاظ على التوافق مع الاستدعاءات القديمة
LINKS = links

def get_nav_metadata():
    """
    إرجاع البيانات الوصفية للموديول لعرضها في لوحة التحكم الرئيسية
    """
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "url": URL_PREFIX,
        "items": NAV_ITEMS,
        "links": links
    }

def register_module(app):
    """
    دالة التسجيل القياسية المعتمدة في مشروع محجوب أونلاين لموديول الرقابة المالية
    """
    try:
        # ✅ التصحيح الجذري هنا: الاستيراد المباشر من مسار الـ routes الفعلي
        from apps.admin_treasury.routes.treasury_controller import admin_treasury_bp
        
        if MODULE_KEY not in app.blueprints:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول الخزينة: {e}")
