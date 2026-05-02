from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# تهيئة المكونات السيادية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ربط المكونات بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # إعدادات حماية الوصول
    login_manager.login_view = 'admin.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى غرفة التحكم."
    login_manager.login_message_category = "info"

    with app.app_context():
        # استيراد الموديلات داخل السياق لضمان تسجيلها في قاعدة البيانات
        from core.models.user import User
        # يمكنك إضافة الموديلات الأخرى هنا (Supplier, Order)

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # تسجيل الـ Blueprint الخاص بالإدارة
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
