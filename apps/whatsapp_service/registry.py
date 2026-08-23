# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

"""
WhatsApp Service Registry Entry for Mahjoub Online
--------------------------------------------------
مسؤول عن تسجيل الموديول في القائمة الجانبية (Sidebar) والـ Blueprints تلقائياً.
"""

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fa-brands fa-whatsapp"  # أو "fa-comments"
SHOW_IN_SUPPLIER = False  # إظهاره في لوحة الإدارة العامة (Admin)

# الروابط التي ستظهر في القائمة الجانبية تحت موديول الواتساب
NAV_ITEMS = [
    {"endpoint": "whatsapp.chat_dashboard", "title": "المحادثات المباشرة"},
    {"endpoint": "whatsapp.logs_dashboard", "title": "سجل الرسائل"},
    {"endpoint": "whatsapp.settings_dashboard", "title": "إعدادات Meta API"},
]

def register_module(app):
    """تسجيل الـ Blueprint وحمايات CSRF الخاصة بالموديول"""
    from apps.whatsapp_service.routes import whatsapp_bp
    from apps.extensions import csrf
    
    # تسجيل الـ Blueprint إذا لم يكن مسجلاً مسبقاً
    if 'whatsapp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        csrf.exempt(whatsapp_bp)
        print("✅ [WhatsApp Registry]: تم تسجيل موديول الواتساب بنجاح عبر Registry.")
