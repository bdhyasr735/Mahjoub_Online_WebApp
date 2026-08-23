# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

"""
تسجيل خدمة واتساب في النظام الرئيسي (القائمة الجانبية والصلاحيات)
"""

MODULE_NAME = 'مركز الواتساب'
MODULE_ICON = 'fa-brands fa-whatsapp'
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {
        'endpoint': 'whatsapp_service.chat_dashboard',
        'title': 'صندوق الرسائل',
        'icon': 'fa-solid fa-comments'
    },
    {
        'endpoint': 'whatsapp_service.logs_dashboard',
        'title': 'سجل الرسائل',
        'icon': 'fa-solid fa-list-check'
    },
    {
        'endpoint': 'whatsapp_service.settings_dashboard',
        'title': 'إعدادات الربط',
        'icon': 'fa-solid fa-gear'
    }
]

# ============================================================
# متغيرات إضافية مطلوبة للنظام الرئيسي
# ============================================================

LINKS = {item['endpoint']: item['title'] for item in NAV_ITEMS}

SERVICE_METADATA = {
    'name': 'whatsapp_service',
    'display_name': MODULE_NAME,
    'icon': MODULE_ICON,
    'admin_menu': NAV_ITEMS,
    'links': LINKS,
    'permissions': [
        'whatsapp.view_chat',
        'whatsapp.send_message',
        'whatsapp.view_logs',
        'whatsapp.admin_settings'
    ]
}

def register_module(app):
    """
    تسجيل موديول الواتساب في التطبيق الرئيسي.
    """
    try:
        # تسجيل في قاموس الخدمات
        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
        app.registered_services['whatsapp_service'] = SERVICE_METADATA
        print("✅ [WhatsApp Module]: تم تسجيل 'مركز الواتساب' في التطبيق الرئيسي.")

        # إضافة إلى ADMIN_MODULES إذا كان موجوداً
        if hasattr(app, 'admin_modules'):
            app.admin_modules['whatsapp_service'] = {
                'display_name': MODULE_NAME,
                'icon': MODULE_ICON,
                'links': LINKS
            }
            print("✅ [WhatsApp Module]: تم إضافة عناصر القائمة إلى ADMIN_MODULES.")

    except Exception as e:
        print(f"❌ [WhatsApp Module]: فشل تسجيل الموديول: {e}")
