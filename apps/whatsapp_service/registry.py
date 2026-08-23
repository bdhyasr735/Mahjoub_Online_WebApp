# coding: utf-8
# 📂 apps/whatsapp_service/registry.py

from apps.whatsapp_service import whatsapp_bp

SERVICE_METADATA = {
    "name": "whatsapp_service",
    "display_name": "خدمة الواتساب",
    "description": "إدارة رسائل العملاء ومحادثات الواتساب",
    "icon": "fa-brands fa-whatsapp",
    "version": "1.0.0"
}

def register_module(app):
    """تسجيل بلوبرنت خدمة الواتساب في تطبيق الفلاسك"""
    app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')
    print("✅ [Registry]: تم تسجيل موديول 'whatsapp_service' بنجاح.")
