# coding: utf-8

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fab fa-whatsapp text-amber-400"

# الطرق المقبولة لقراءة الروابط في الكود لديك:
LINKS = {
    'whatsapp.chat_dashboard': 'المحادثات المباشرة',
    'whatsapp.logs_dashboard': 'سجل الرسائل',
    'whatsapp.settings_dashboard': 'إعدادات الربط'
}

def register_module(app):
    # إذا كان لديك Blueprints خاصة بالواتساب يتم تسجيلها هنا
    pass
