# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": "خدمة الواتساب",
    "description": "إدارة رسائل العملاء ومحادثات الواتساب",
    "icon": "fa-brands fa-whatsapp",
    "version": "1.0.0"
}

def register_module(app):
    """تسجيل بلوبرنت الواتساب من ملف dashboard محلياً لتجنب الاستيراد الدائري"""
    try:
        from apps.whatsapp_service.routes.dashboard import whatsapp_bp
        app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
        print("✅ [Registry]: تم تسجيل موديول 'whatsapp_service' بنجاح.")
    except Exception as e:
        print(f"❌ [Registry]: خطأ في تسجيل موديول 'whatsapp_service': {e}")
        raise e
