# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

"""
WhatsApp Service Registry Entry for Mahjoub Online
--------------------------------------------------
مسؤول عن تسجيل الموديول والروابط الخاصة به تلقائياً في القائمة الجانبية (Sidebar) والهيكل العام للنظام.
"""

# الاسم الظاهر في القائمة الجانبية
MODULE_NAME = "خدمة الواتساب"

# الأيقونة الخاصة بالموديول (FontAwesome)
MODULE_ICON = "fa-brands fa-whatsapp"

# لتحديد ما إذا كان الموديول يظهر في لوحة الموردين أم لوحة الإدارة (False = Admin)
SHOW_IN_SUPPLIER = False

# الروابط الفرعية التي ستظهر داخل قائمة الموديول في القائمة الجانبية
NAV_ITEMS = [
    {"endpoint": "whatsapp.chat_dashboard", "title": "المحادثات المباشرة"},
    {"endpoint": "whatsapp.logs_dashboard", "title": "سجل الرسائل"},
    {"endpoint": "whatsapp.settings_dashboard", "title": "إعدادات Meta API"},
]


def register_module(app):
    """دالة تسجيل الـ Blueprint وإعفائه من CSRF تلقائياً عند تشغيل النظام"""
    from apps.whatsapp_service.routes import whatsapp_bp
    from apps.extensions import csrf

    if 'whatsapp' not in app.blueprints:
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        csrf.exempt(whatsapp_bp)
        print("✅ [WhatsApp Registry]: تم تسجيل موديول الواتساب بنجاح عبر Registry.")
