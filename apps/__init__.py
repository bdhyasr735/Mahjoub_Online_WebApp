# coding: utf-8
# 🛡️ المحرك المركزي لمنصة محجوب أونلاين 2026
# التوثيق: المصنع الرئيسي (App Factory) لإدارة الدروع الأمنية وقواعد البيانات

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# 1. تهيئة المحركات البرمجية (Global Instances)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """
    دالة إنشاء التطبيق (App Factory)
    """
    app = Flask(__name__)

    # 2. الإعدادات السيادية للمنصة (Railway Environment)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_key_2026')
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # 3. ربط المحركات بالتطبيق الفعلي
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app) 

    # إعدادات نظام الولوج
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    # 4. تسجيل الأقسام البرمجية (Blueprints) - التعديل المطلوب هنا
    # الاستيراد من المسار الكامل لضمان عدم حدوث ModuleNotFoundError
    from apps.auth_portal.routes import auth_bp
    # تأكد من أن أسماء المتغيرات (Blueprints) تطابق ما عرفته داخل تطبيقاتك
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers 
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    # 5. بناء جدار قاعدة البيانات (Database Sync)
    with app.app_context():
        try:
            # استيراد النماذج من المسار الموحد لضمان تسجيل الجداول
            import apps.models 
            db.create_all()
            print("✅ تم تعميد جداول قاعدة البيانات بنجاح.")
        except Exception as e:
            print(f"⚠️ تنبيه: السيرفر يعمل ولكن تعذر تحديث الجداول تلقائياً: {e}")

    return app

# تعريف مستخدم النظام لـ Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # استخدام استيراد مطلق هنا أيضاً لمنع تعليق السيرفر
    from apps.models.admin_db import AdminUser
    try:
        return AdminUser.query.get(int(user_id))
    except:
        return None
