# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

MODULE_KEY = "admin_treasury"
DISPLAY_NAME = "الرقابة المالية"
ICON = "landmark"
VERSION = "2.4.0"
URL_PREFIX = "/admin/treasury"
REQUIRED_PERMISSION = "manage_platform_treasury"

# عناصر القائمة الجانبية (Nav Items)
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
        "items": NAV_ITEMS
    }

def register_module(app):
    """
    دالة التسجيل القياسية المعتمدة في مشروع محجوب أونلاين لموديول الرقابة المالية
    """
    # استيراد البلوبرنت داخل الدالة لتجنب الاستيراد الدائري (Circular Import)
    from apps.admin_treasury import admin_treasury_bp
    
    # تسجيل الموديول إذا لم يكن مسجلاً مسبقاً
    if MODULE_KEY not in app.blueprints:
        try:
            app.register_blueprint(admin_treasury_bp, url_prefix=URL_PREFIX)
            print(f"[*] Module {DISPLAY_NAME} registered successfully at {URL_PREFIX}")
        except Exception as e:
            print(f"[!] Failed to register module {MODULE_KEY}: {e}")
