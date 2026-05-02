from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# تعريف الأدوات الأساسية للترسانة الرقمية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة الإضافات وربطها بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # تحديد بوابة الدخول الرئيسية للإدارة
    # تأكد أن اسم الـ endpoint هو 'admin_login' داخل 'admin_bp'
    login_manager.login_view = 'admin.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة."

    # الاستيراد داخل الدالة لمنع التكرار وخطأ "MetaData instance"
    from core.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        # البحث عن القائد في قاعدة البيانات
        return User.query.get(int(user_id))

    # تسجيل الـ Blueprints
    # تأكد من استيراد admin_bp من المسار الصحيح
    try:
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError as e:
        print(f"⚠️ تحذير: فشل تحميل Blueprint الإدارة: {e}")

    return app
