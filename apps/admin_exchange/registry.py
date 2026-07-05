# 📂 apps/exchange/registry.py
from apps.exchange.exchange_routes import admin_exchange_bp

def register_module(app):
    app.register_blueprint(admin_exchange_bp, url_prefix='/admin/exchange')
    print("✅ [Registry]: تم تسجيل موديول 'Exchange' بنجاح.")
