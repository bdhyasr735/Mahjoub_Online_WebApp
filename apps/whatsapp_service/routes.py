def register_module(app):
    """
    تسجيل موديول الواتساب في تطبيق Flask / Python المركزي.
    """
    try:
        # استيراد المسارات من ملف routes.py
        from apps.whatsapp_service.routes import whatsapp_bp, webhook_public_bp
        
        # استيراد CSRF من ملف الإضافات
        from apps.extensions import csrf

        # تسجيل مسار لوحة التحكم الإدارية
        if whatsapp_bp.name not in app.blueprints:
            app.register_blueprint(whatsapp_bp)
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' بنجاح تحت المسار {URL_PREFIX}.")

        # تسجيل المسار العام /whatsapp/webhook (لحل مشكلة الـ 404)
        if webhook_public_bp.name not in app.blueprints:
            app.register_blueprint(webhook_public_bp)
            print(f"✅ [Module]: تم تسجيل مسار الـ Webhook العام '/whatsapp/webhook' بنجاح.")

        # 🔥 الأهم: استثناء المسارات من حماية CSRF (حتى تصل رسائل Meta)
        csrf.exempt(whatsapp_bp)
        csrf.exempt(webhook_public_bp)

    except ImportError:
        # في حالة الاستيراد النسبي
        try:
            from .routes import whatsapp_bp, webhook_public_bp
            from apps.extensions import csrf
            
            if whatsapp_bp.name not in app.blueprints:
                app.register_blueprint(whatsapp_bp)
            
            if webhook_public_bp.name not in app.blueprints:
                app.register_blueprint(webhook_public_bp)
                
            csrf.exempt(whatsapp_bp)
            csrf.exempt(webhook_public_bp)
            
            print(f"✅ [Module]: تم تسجيل موديول '{MODULE_NAME}' (استيراد نسبي) وتفعيله بنجاح.")
        except Exception as inner_e:
            print(f"❌ [Module Error]: فشل استيراد موديول الواتساب. تفاصيل: {inner_e}")
    except Exception as e:
        print(f"❌ [Module Error]: تعذر تسجيل موديول الواتساب. تفاصيل: {e}")
