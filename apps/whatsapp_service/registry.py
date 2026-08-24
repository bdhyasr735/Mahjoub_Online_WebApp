# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"

# مطابقة أسماء الدوال الفعلية في ملف dashboard.py لتجنب خطأ عدم التحويل
LINKS = {
    'whatsapp_service.chat_dashboard': 'إدارة مراسلات الواتساب',
    'whatsapp_service.settings_dashboard': 'إعدادات الواتساب'
}

def register_module(app):
    """
    تسجيل بلوبرنت الواتساب تلقائياً في التطبيق الرئيسي بأمان تام
    """
    try:
        from apps.whatsapp_service.routes import whatsapp_bp
        
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("🟢 [WhatsApp Registry]: ✅ تم تسجيل موديول الواتساب والمسارات بنجاح تام.")
    except Exception as e:
        print(f"🔴 [WhatsApp Registry Error]: ❌ فشل تسجيل موديول الواتساب - السبب: {e}")