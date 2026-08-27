# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py
"""
تسجيل موديول خدمة مراسلات الواتساب الذكية (Meta WhatsApp Cloud API v26.0)
في نظام التسجيل المركزي والديناميكي للمشروع
Mahjoub Online WebApp
"""

# ========== بيانات الموديول الأساسية ==========
MODULE_KEY = "whatsapp_service"
MODULE_NAME = "خدمة الواتساب"
DISPLAY_NAME = "مراسلات الواتساب"
MODULE_ICON = "fab fa-whatsapp"
ICON = "whatsapp"
VERSION = "2.6.0"
URL_PREFIX = "/admin/whatsapp"
REQUIRED_PERMISSION = "manage_whatsapp_service"

# ✅ تفعيل الظهور التلقائي في القائمة الجانبية للوحة التحكم
SHOW_IN_ADMIN = True
SHOW_IN_SUPPLIER = False

# ========== روابط القائمة الجانبية الديناميكية ==========
LINKS = {
    "whatsapp_service.dashboard_view": "المحادثات المباشرة",
    "whatsapp_service.contacts_bulk_view": "جهات الاتصال والإرسال الجماعي",
    "whatsapp_service.templates_view": "قوالب ميتا المعتمدة",
    "whatsapp_service.webhook_logs_view": "سجل تدفق الويب هوك",
    "whatsapp_service.settings_view": "إعدادات Meta Cloud API",
}

links = LINKS


def get_nav_metadata():
    """
    إرجاع الميتا داتا الديناميكية لبناء عنصر القائمة الجانبية (Sidebar) تلقائياً
    """
    return {
        "key": MODULE_KEY,
        "name": DISPLAY_NAME,
        "icon": ICON,
        "module_icon": MODULE_ICON,
        "url": URL_PREFIX + "/dashboard",
        "items": [
            {
                "title": "المحادثات المباشرة",
                "url": URL_PREFIX + "/dashboard",
                "icon": "fas fa-comments"
            },
            {
                "title": "📇 جهات الاتصال والإرسال الجماعي",
                "url": URL_PREFIX + "/contacts-bulk",
                "icon": "fas fa-address-book"
            },
            {
                "title": "قوالب ميتا المعتمدة",
                "url": URL_PREFIX + "/templates",
                "icon": "fas fa-layer-group"
            },
            {
                "title": "سجل الويب هوك (Live)",
                "url": URL_PREFIX + "/webhook-logs",
                "icon": "fas fa-stream"
            },
            {
                "title": "الإعدادات والربط السحابي",
                "url": URL_PREFIX + "/settings",
                "icon": "fas fa-sliders-h"
            }
        ],
        "links": links,
        "show_in_admin": SHOW_IN_ADMIN,
        "version": VERSION
    }


def register_module(app):
    """
    تسجيل موديول الواتساب في تطبيق Flask / Python المركزي.
    """
    try:
        # استيراد المسارات من ملف routes.py (يحتوي على كل شيء بما فيه جهات الاتصال)
        from apps.whatsapp_service.routes import whatsapp_bp, webhook_public_bp
        
        # استيراد CSRF من ملف الإضافات
        from apps.extensions import csrf

        # تسجيل مسار لوحة التحكم الإدارية (يحتوي على /dashboard و /contacts-bulk)
        if whatsapp_bp.name not in app.blueprints:
            app.register_blueprint(whatsapp_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
            print(f"✅ [Module]: تم تفعيل مسارات جهات الاتصال '/contacts-bulk' تلقائياً.")

        # تسجيل المسار العام /whatsapp/webhook (لحل مشكلة الـ 404)
        if webhook_public_bp.name not in app.blueprints:
            app.register_blueprint(webhook_public_bp)
            print(f"✅ [Module]: تم تسجيل مسار الـ Webhook العام '/whatsapp/webhook' بنجاح.")

        # 🔥 الأهم: استثناء المسارات من حماية CSRF (حتى تصل رسائل Meta)
        csrf.exempt(whatsapp_bp)
        csrf.exempt(webhook_public_bp)

    except ImportError:
        # في حالة الاستيراد النسبي
        try:
            from .routes import whatsapp_bp, webhook_public_bp
            from apps.extensions import csrf
            
            if whatsapp_bp.name not in app.blueprints:
                app.register_blueprint(whatsapp_bp)
            
            if webhook_public_bp.name not in app.blueprints:
                app.register_blueprint(webhook_public_bp)
            
            csrf.exempt(whatsapp_bp)
            csrf.exempt(webhook_public_bp)
            
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' (استيراد نسبي) وتفعيله بنجاح.")
        except Exception as inner_e:
            print(f"❌ [Module Error]: فشل استيراد موديول الواتساب. تفاصيل: {inner_e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول الواتساب. تفاصيل: {e}")


def register_service(app):
    register_module(app)
