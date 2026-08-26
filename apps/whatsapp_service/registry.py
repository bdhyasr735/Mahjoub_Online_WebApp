def register_module(app):
    """
    تسجيل موديول الواتساب في تطبيق Flask / Python المركزي
    """
    try:
        from apps.whatsapp_service.routes import whatsapp_bp, webhook_public_bp
        from apps.extensions import csrf  # استيراد CSRF
        
        # تسجيل مسار لوحة التحكم الإدارية
        if whatsapp_bp.name not in app.blueprints:
            app.register_blueprint(whatsapp_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")
        
        # تسجيل المسار العام (لحل مشكلة الـ 404) 🔥
        if webhook_public_bp.name not in app.blueprints:
            app.register_blueprint(webhook_public_bp)
            print(f"✅ [Module]: تم تسجيل مسار الـ Webhook العام '/whatsapp/webhook' بنجاح.")

        # 🔥 استثناء المسارات من حماية CSRF (أهم خطوة)
        csrf.exempt(whatsapp_bp)
        csrf.exempt(webhook_public_bp)

    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول الواتساب. تفاصيل: {e}")
