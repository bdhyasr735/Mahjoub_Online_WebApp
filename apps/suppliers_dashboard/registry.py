# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True

LINKS = {
    'suppliers_dashboard.dashboard': '📊 لوحة التحكم',
    'suppliers_wallet.withdraw': '💳 سحب الرصيد',
    'suppliers_settings.settings': '⚙️ إعدادات المتجر'
}


def register_module(app):
    # ✅ استيراد من المسار الصحيح (مع routes)
    from apps.suppliers_dashboard.routes.dashboard_routes import suppliers_dashboard_bp
    from apps.suppliers_dashboard.routes.settings_routes import settings_bp
    from apps.suppliers_dashboard.routes.wallet_routes import wallet_bp
    
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_dashboard' بنجاح.")
    
    if 'suppliers_settings' not in app.blueprints:
        app.register_blueprint(settings_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_settings' بنجاح.")
    
    if 'suppliers_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_wallet' بنجاح.")
    
    return app
