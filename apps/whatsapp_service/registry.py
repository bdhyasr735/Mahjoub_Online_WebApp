# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"

# الروابط التي تظهر في لوحة التحكم الإدارية
LINKS = {
    'whatsapp_service.dashboard_index': 'إدارة مراسلات الواتساب',
    'whatsapp_service.settings_view': 'إعدادات الواتساب'
}

def register_module(app):
    """
    تسجيل بلوبرنت الواتساب تلقائياً في التطبيق الرئيسي بأمان تام
    """
    try:
        # استيراد الـ Blueprint محلياً من مجلد المسارات لتجنب أي تداخل
        from apps.whatsapp_service.routes import whatsapp_bp
        
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("🟢 [WhatsApp Registry]: ✅ تم تسجيل موديول الواتساب والمسارات بنجاح تام.")
    except Exception as e:
        print(f"🔴 [WhatsApp Registry Error]: ❌ فشل تسجيل موديول الواتساب - السبب: {e}")
