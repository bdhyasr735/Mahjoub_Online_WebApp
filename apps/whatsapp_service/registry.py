# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = 'مركز الواتساب'
MODULE_ICON = 'fa-brands fa-whatsapp'
SHOW_IN_SUPPLIER = False

NAV_ITEMS = [
    {
        'endpoint': 'whatsapp_controller.index',
        'title': 'صندوق الرسائل'
    },
    {
        'endpoint': 'whatsapp_controller.settings',
        'title': 'إعدادات الربط'
    }
]

def register_module(app):
    """
    هنا لأنك قمت بتسجيل الـ Blueprint سابقاً لا نحتاج لتسجيل الـ
    CSRF مع استثنائه من __init__.py بشكل صريح في ملف
    """
    pass
