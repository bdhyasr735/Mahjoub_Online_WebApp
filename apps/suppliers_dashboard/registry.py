# ============================================================
    # 🔌 التسجيل اليدوي لموديول لوحة تحكم الموردين
    # ============================================================
    try:
        from apps.suppliers_dashboard import suppliers_dashboard_bp
        if 'suppliers_dashboard_core' not in app.blueprints:
            app.register_blueprint(suppliers_dashboard_bp)
            print("✅ [لوحة تحكم الموردين]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ لوحة تحكم الموردين]: فشل تسجيل الموديول: {e}")
