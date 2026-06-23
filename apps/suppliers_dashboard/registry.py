def register_app(app):
    """
    تسجيل مسارات الموردين بشكل آمن (Lazy Import).
    لن يتم استيراد routes.py إلا إذا نجح النظام، ولن يوقف الإدارة إذا فشل.
    """
    try:
        # نقوم بالاستيراد هنا داخل الدالة (داخل الـ try)
        # إذا فشل الاستيراد، سيذهب للـ except ولن ينهار المصنع الرئيسي
        from apps.suppliers_dashboard.routes import dashboard_bp
        
        app.register_blueprint(dashboard_bp, url_prefix='/suppliers_dashboard')
        print("✅ [Registry] تم تسجيل وحدة لوحة تحكم المورد بنجاح.")
        
    except Exception as e:
        # هنا يتم التقاط الخطأ (مثل cannot import name 'VendorAuthService')
        # وطباعته دون أن يؤثر على عمل الإدارة في المصنع الرئيسي
        print(f"⚠️ [Registry] تعذر تحميل لوحة تحكم المورد: {e}")
