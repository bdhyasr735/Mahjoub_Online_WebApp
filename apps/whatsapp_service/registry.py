def register_module(app):
    """
    تسجيل موديول الواتساب في تطبيق Flask / Python المركزي.
    هذه الدالة مسؤولة عن تسجيل المسارات الإدارية والعامة، واستثنائهم من CSRF.
    """
    try:
        # جلب الـ Blueprints من ملف Routes
        from apps.whatsapp_service.routes import whatsapp_bp, webhook_public_bp
        
        # تسجيل مسار لوحة التحكم الإدارية
        if whatsapp_bp.name not in app.blueprints:
            app.register_blueprint(whatsapp_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")

        # تسجيل المسار العام /whatsapp/webhook (لحل مشكلة الـ 404)
        if webhook_public_bp.name not in app.blueprints:
            app.register_blueprint(webhook_public_bp)
            print(f"✅ [Module]: تم تسجيل مسار الـ Webhook العام '/whatsapp/webhook' بنجاح.")

        # 🔥 الأهم: استثناء المسارات من حماية CSRF (حتى تصل رسائل Meta)
        from apps.extensions import csrf
        csrf.exempt(whatsapp_bp)
        csrf.exempt(webhook_public_bp)

    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول الواتساب. تفاصيل: {e}")
