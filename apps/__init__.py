# apps/__init__.py
from flask import Flask
from apps.extensions import db, login_manager # استيراد من الملف الجديد
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # ... (باقي كود الإعدادات الخاص بك)
    
    # استيراد الـ Blueprints هنا بعد تهيئة التطبيق
    from apps.admin_dashboard import admin_dashboard_bp
    from apps.add_supplier import admin_suppliers_bp
    
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    
    return app
