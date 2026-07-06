# في apps/suppliers_dashboard/registry.py
def register_module(app):
    """
    تسجيل الموديول بطريقة آمنة جداً.
    """
    # التحقق من وجوده في المسجلين مسبقاً
    if not any(bp.name == 'suppliers_dashboard' for bp in app.blueprints.values()):
        app.register_blueprint(suppliers_dashboard_bp)
        print("✅ [Registry]: تم تسجيل موديول 'suppliers_dashboard' بنجاح.")
