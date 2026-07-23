# coding: utf-8
# 📂 apps/suppliers_dashboard/registry.py

"""
تسجيل تطبيق لوحة تحكم الموردين في المنصة
"""

# ✅ بيانات الموديول
MODULE_NAME = "لوحة التحكم"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True  # ✅ يظهر في قائمة المورد

# ✅ الروابط التي تظهر في القائمة الجانبية للمورد
LINKS = {
    'suppliers_dashboard.dashboard': '📊 لوحة التحكم',
    'suppliers_wallet.withdraw': '💳 سحب الرصيد',
    'suppliers_settings.settings': '⚙️ إعدادات المتجر'
}


def register_module(app):
    """
    تسجيل موديول لوحة التحكم (Dashboard) في التطبيق الرئيسي
    """
    # ✅ استيراد مباشر من الملفات في المجلد الرئيسي
    from apps.suppliers_dashboard.dashboard_routes import suppliers_dashboard_bp
    from apps.suppliers_dashboard.settings_routes import settings_bp
    from apps.suppliers_dashboard.wallet_routes import wallet_bp
    from apps.suppliers_dashboard.ai_routes import ai_bp
    
    # ✅ تسجيل Blueprint لوحة التحكم
    if 'suppliers_dashboard' not in app.blueprints:
        app.register_blueprint(suppliers_dashboard_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_dashboard' بنجاح.")
    
    # ✅ تسجيل Blueprint الإعدادات
    if 'suppliers_settings' not in app.blueprints:
        app.register_blueprint(settings_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_settings' بنجاح.")
    
    # ✅ تسجيل Blueprint المحفظة
    if 'suppliers_wallet' not in app.blueprints:
        app.register_blueprint(wallet_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'suppliers_wallet' بنجاح.")
    
    # ✅ تسجيل Blueprint مساعد الذكاء الاصطناعي
    if 'ai_bp' not in app.blueprints:
        app.register_blueprint(ai_bp, url_prefix='/supplier')
        print("✅ [Registry]: تم تسجيل 'ai_bp' بنجاح.")
    
    return app
