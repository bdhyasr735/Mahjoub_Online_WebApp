"""
Dynamic Service Registry for WhatsApp Service
"""

def register_module(app):
    """
    تسجيل ديناميكي للموديول وربطه بنظام القوائم (Sidebar)
    """
    try:
        from apps.whatsapp_service.routes.whatsapp_controller import whatsapp_bp
        
        # تسجيل الـ Blueprint ببادئة إدارية ثابتة
        app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        
        # إضافة الموديول لقائمة الخدمات المسجلة في التطبيق
        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
            
        app.registered_services['whatsapp_service'] = {
            "name": "whatsapp_service",
            "display_name": "خدمة مراسلات واتساب محجوب أونلاين",
            "admin_menu": [
                {"title": "محادثات العملاء", "endpoint": "whatsapp_service.chat_dashboard", "icon": "fas fa-comments"},
                {"title": "سجل الرسائل", "endpoint": "whatsapp_service.logs_dashboard", "icon": "fas fa-database"},
                {"title": "إعدادات Meta Cloud API", "endpoint": "whatsapp_service.settings_dashboard", "icon": "fas fa-cog"}
            ]
        }
        print("✅ [Module]: تم تسجيل 'whatsapp_service' ديناميكياً بنجاح.")
        
    except Exception as e:
        print(f"❌ [Module]: خطأ في تسجيل 'whatsapp_service': {e}")
