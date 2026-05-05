# core/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# 1. تهيئة أدوات النظام الأساسية (خارج الدالة لضمان الوصول إليها من الموديلات)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # إنشاء تطبيق Flask
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # تحميل الإعدادات من كائن Config
    app.config.from_object('config.Config')
    
    # 2. ربط قاعدة البيانات ونظام الدخول بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)

    # إعدادات حماية الجلسة
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى منطقة الإدارة السيادية."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- 3. استيراد الموديلات لضمان تسجيل الجداول ---
        # استيراد الموردين والمستخدمين داخل السياق لمنع أخطاء Import
        from core.models.user import User
        from core.models.supplier import Supplier # الموديل الجديد لـ محجوب أونلاين

        # --- 4. تسجيل الـ Blueprints ---
        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        # --- 5. محمل المستخدم (User Loader) ---
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # إنشاء الجداول إذا لم تكن موجودة (اختياري لكن مفيد في Railway)
        # db.create_all() 

    return app
