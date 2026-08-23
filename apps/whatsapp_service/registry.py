# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

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

def register_module(app):
    pass
