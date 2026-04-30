import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# تهيئة الإضافات
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # إعدادات قاعدة البيانات - منصة محجوب أونلاين 2026
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "Ali_Mahjoub_Sovereign_2026")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تفعيل الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'admin_panel.admin_login'

    with app.app_context():
        # التعديل الذهبي لحل مشكلة unknown location:
        # نقوم باستيراد المجلد كحزمة كاملة ثم نأخذ منها البلوبرنت
        import admin_panel
        app.register_blueprint(admin_panel.admin_panel, url_prefix='/admin')

        # استدعاء الموديلات لضمان بناء الجداول
        from core import models

    return app

@login_manager.user_loader
def load_user(user_id):
    from core.models import User
    return User.query.get(int(user_id))
