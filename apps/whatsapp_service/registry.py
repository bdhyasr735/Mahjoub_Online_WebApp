def register_module(app):
    """
    تسجيل موديول الواتساب ومساراته تلقائياً في التطبيق الرئيسي
    """
    try:
        from apps.whatsapp_service.routes.whatsapp_controller import whatsapp_bp
        
        # تسجيل الـ Blueprint إذا لم يكن مسجلاً من قبل لتجنب التكرار
        if 'whatsapp_service' not in app.blueprints:
            app.register_blueprint(whatsapp_bp, url_prefix='/admin/whatsapp')
        
        # 🔗 استيراد وإنشاء الجداول في قاعدة البيانات تلقائياً
        with app.app_context():
            from apps.whatsapp_service.models import whatsapp_models  # أو المسار الصحيح لاستيراد الموديلات
            # إذا كنت تستخدم db المعرفة في app الرئيسي:
            try:
                from app import db
                db.create_all()
            except ImportError:
                pass

        # تسجيل بيانات الموديول والخدمة في التطبيق
        if not hasattr(app, 'registered_services'):
            app.registered_services = {}
            
        app.registered_services['whatsapp_service'] = SERVICE_METADATA
        print("✅ [Module]: تم تسجيل 'whatsapp_service' ومساراته والجداول بنجاح.")
        
    except Exception as e:
        print(f"❌ [Module]: خطأ في تسجيل 'whatsapp_service': {e}")
