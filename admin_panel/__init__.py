# core/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# تعريف المحركات الأساسية للترسانة الرقمية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # إعدادات السيادة (تأكد من ضبطها في بيئة Railway)
    app.config['SECRET_KEY'] = 'mahjoub_sovereign_secret_2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...' # أو جلبها من env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تفعيل المحركات
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى الترسانة السيادية"

    with app.app_context():
        # استيراد النماذج (Models) لضمان تسجيلها في SQLAlchemy
        from core.models.user import User
        from core.models.vendor import Vendor
        
        # تسجيل الـ Blueprints
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        # استدعاء دالة ترميم الهوية (اختياري عند كل تشغيل)
        # db.create_all() 

    return app

@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    return User.query.get(int(user_id))
