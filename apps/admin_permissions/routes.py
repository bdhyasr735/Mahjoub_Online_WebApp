# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"

# استخدام اسم الدالة القياسي 'index' تماماً مثل بقية الموديولات الناجحة
LINKS = {
    'whatsapp_service.index': 'إدارة مراسلات الواتساب',
    'whatsapp_service.settings_dashboard': 'إعدادات الواتساب'
}

def register_module(app):
    try:
        from apps.whatsapp_service.routes import whatsapp_bp
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("🟢 [WhatsApp Registry]: ✅ تم تسجيل موديول الواتساب بنجاح.")
    except Exception as e:
        print(f"🔴 [WhatsApp Registry Error]: ❌ {e}")