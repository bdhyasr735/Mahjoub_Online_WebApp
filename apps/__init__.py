# apps/__init__.py
from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # معالجة الـ Proxy لبيئات الإنتاج (مهم جداً لـ Railway)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # استيراد البلوبرينتس هنا داخل السياق
        from apps.auth_portal.routes import auth_blueprint
        from apps.admin_dashboard.routes import admin_dashboard
        # أضف بقية البلوبرينتس هنا
        
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(admin_dashboard)
        
        db.create_all()

    return app

app = create_app()
