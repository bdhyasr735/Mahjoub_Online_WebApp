def register_module(app):
    """
    تسجيل موديول الواتساب ومساراته تلقائياً
    """
    try:
        from .routes.whatsapp_controller import whatsapp_bp
        
        # التأكد من عدم تسجيل الـ Blueprint مسبقاً لتجنب الأخطاء
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
            print("✅ [WhatsApp Module]: تم تسجيل الـ Blueprint بنجاح على /admin/whatsapp")
            
    except Exception as e:
        print(f"❌ [WhatsApp Module Error]: {e}")
