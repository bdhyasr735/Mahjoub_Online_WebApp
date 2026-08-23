# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = 'مركز الواتساب'
MODULE_ICON = 'fa-brands fa-whatsapp'  # أيقونة الواتساب من FontAwesome
SHOW_IN_SUPPLIER = False  # إخفاء من لوحة الموردين وعرضه في الإدارة المركزية فقط

# تحديد الروابط التي ستظهر تحت هذه القائمة
NAV_ITEMS = [
    {
        'endpoint': 'whatsapp_controller.index',  # استبدل index باسم الدالة الرئيسية للواجهة لديك
        'title': 'صندوق الرسائل'
    },
    {
        'endpoint': 'whatsapp_controller.settings', # استبدل settings باسم دالة الإعدادات إن وجدت
        'title': 'إعدادات الربط'
    }
]

def register_module(app):
    """
    لا نحتاج لتسجيل الـ Blueprint هنا لأنك قمت بتسجيله مسبقاً 
    بشكل صريح في ملف __init__.py مع استثنائه من CSRF
    """
    pass
