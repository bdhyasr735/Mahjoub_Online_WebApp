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

# ✅ التصحيح هنا: جعل المدى يطابق ما يبحث عنه القالب (module.links)
links = {
    "admin_treasury.treasury_index": "إدارة الخزينة والقيود"
}

LINKS = links # للحفاظ على توافق أي استدعاء قديم

NAV_ITEMS = [
    {
        "id": "treasury_overview",
        "title": "إدارة الخزينة والقيود",
        "endpoint": "admin_treasury.treasury_index",
        "icon": "wallet",
        "permission": "view_treasury"
    }
]

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
        "links": links  # ✅ إضافة الروابط هنا أيضاً لتراها لوحة التحكم الرئيسية مباشرة
    }

def register_module(app):
    """
    دالة التسجيل القياسية المعتمدة في مشروع محجوب أونلاين لموديول الرقابة المالية
    """
    from apps.admin_treasury import admin_treasury_bp
    
    if MODULE_KEY not in app.blueprints:
        try:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print("✅ [Registry]: تم تسجيل موديول 'الخزينة' بنجاح.")
        except Exception as e:
            print(f"❌ [Registry Error]: فشل تسجيل موديول الخزينة: {e}")
