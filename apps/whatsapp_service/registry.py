# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

MODULE_NAME = "خدمة الواتساب"
MODULE_ICON = "fas fa-comments"

LINKS = {
    '/admin/whatsapp/': 'إدارة مراسلات الواتساب',
    '/admin/whatsapp/logs': 'سجلات النظام',
    '/admin/whatsapp/settings': 'إعدادات الواتساب'
}

def register_module(app):
    """تسجيل بلوبرنت الواتساب تلقائياً مع طباعة حالة النجاح أو الفشل بوضوح"""
    try:
        from apps.whatsapp_service.routes import whatsapp_bp
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("🟢 [WhatsApp Registry]: ✅ تم تسجيل موديول الواتساب بنجاح تام في النظام الديناميكي.")
        else:
            print("🟡 [WhatsApp Registry]: ⚠️ موديول الواتساب مسجل مسبقاً.")
    except Exception as e:
        print(f"🔴 [WhatsApp Registry Error]: ❌ فشل تسجيل موديول الواتساب - السبب: {e}")
