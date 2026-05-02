from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# تهيئة الكائنات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # بديل CORS: إضافة رؤوس الاستجابة يدويًا للسماح بالطلبات المتقاطعة
    # هذا يغنيك عن مكتبة flask-cors ويحل مشكلة اتصال السيرفر
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    # ربط الإضافات بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    
    # إعدادات نظام تسجيل الدخول
    # تم ضبطها لتتوافق مع "admin.login" في ملف routes.py
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    with app.app_context():
        # استيراد النماذج لضمان تعريفها في قاعدة البيانات
        from core.models.user import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # تسجيل الـ Blueprints (لوحة التحكم الإدارية)
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
