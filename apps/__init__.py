# apps/__init__.py
from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # تسجيل البلوبرينتس (تأكد من صحة مسارات الاستيراد)
        from apps.wallet.routes import wallet_blueprint
        app.register_blueprint(wallet_blueprint, url_prefix='/wallet')

        from apps.auth_portal.routes import auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from apps.admin_dashboard.routes import admin_dashboard
        app.register_blueprint(admin_dashboard)

        db.create_all()

    return app

app = create_app()
