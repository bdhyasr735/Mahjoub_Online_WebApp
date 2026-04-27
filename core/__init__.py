# داخل دالة create_app()
    with app.app_context():
        try:
            # استخدام الاستيراد المطلق (Absolute Import)
            import admin_panel
            import supplier_panel
            
            app.register_blueprint(admin_panel.admin_bp, url_prefix='/admin')
            app.register_blueprint(supplier_panel.supplier_bp, url_prefix='/supplier')
            
            print("✅ [Success] تم تعميد البوابات بنجاح سيادي.")
        except Exception as e:
            print(f"❌ [Error] Blueprint registration failed: {e}")
            # لإظهار الخطأ الكامل في Logs
            import traceback
            traceback.print_exc()
