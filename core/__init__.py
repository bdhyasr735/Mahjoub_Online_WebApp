from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# تهيئة أدوات النظام الأساسية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # إنشاء تطبيق Flask
    app = Flask(__name__)
    
    # تحميل الإعدادات من كائن Config
    app.config.from_object('config.Config')
    
    # ربط قاعدة البيانات ونظام الدخول بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)

    # إعدادات حماية الجلسة وتوجيه المتطفلين
    login_manager.login_view = 'admin.login'  # البوابة التي يتم تحويل غير المسجلين إليها
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى منطقة الإدارة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 1. تسجيل الـ Blueprints (الربط المركزي) ---
        # استيراد وتسجيل لوحة التحكم ببادئة /admin
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # يمكنك تسجيل مسارات الموقع الرئيسي هنا لاحقاً
        # from . import routes

        # --- 2. محمل المستخدم (The User Loader) ---
        # هذا الجزء حيوي جداً لعمل @login_required في routes.py
        from core.models.user import User
        
        @login_manager.user_loader
        def load_user(user_id):
            """يستخدمه Flask-Login لاستعادة كائن المستخدم من قاعدة البيانات عبر الـ ID"""
            return User.query.get(int(user_id))

    return app
