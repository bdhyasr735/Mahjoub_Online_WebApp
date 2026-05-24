from flask import Flask
from apps.extensions import db, login_manager
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    # استخدام app_context لكسر حلقة الاستيراد
    with app.app_context():
        # استيراد الموديلات هنا فقط
        from apps.models.admin_db import AdminUser
        
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # استيراد وتسجيل البلوبرينتس هنا فقط
        from apps.auth_portal.routes import auth_blueprint
        from apps.admin_dashboard.routes import admin_dashboard
        from apps.add_supplier.routes import admin_suppliers_bp
        from apps.wallet.routes import wallet_blueprint

        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(admin_dashboard)
        app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
        app.register_blueprint(wallet_blueprint, url_prefix='/wallet')

        db.create_all()

    return app

# لا تقم بإنشاء المتغير app هنا إذا كنت تستخدم gunicorn مباشرة في Railway
# دع Gunicorn يستدعي المصنع من خلال ملف التشغيل (run.py)
