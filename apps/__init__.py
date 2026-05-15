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
    تقوم بتجميع القطع البرمجية وتفعيل الدروع الأمنية
    """
    app = Flask(__name__)

    # 2. الإعدادات السيادية للمنصة (Railway Environment)
    # مفتاح التشفير لجلسات المستخدمين ودروع CSRF
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_key_2026')
    
    # معالجة رابط قاعدة البيانات ليتوافق مع معايير SQLAlchemy 1.4+ و PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تحسين استقرار الاتصال بقاعدة البيانات في البيئات السحابية
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # 3. ربط المحركات بالتطبيق الفعلي
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app) 

    # إعدادات نظام الولوج (Flask-Login)
    # ملاحظة: تم ضبطها لتطابق مسار auth_bp الذي سجلناه بالأسفل
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    # 4. تسجيل الأقسام البرمجية (Blueprints)
    # تم استخدام الاستيراد المطلق (Absolute Import) لمنع خطأ ModuleNotFoundError في Railway
    try:
        from apps.auth_portal.routes import auth_bp
        from apps.admin_dashboard.routes import admin_dashboard
        from apps.add_supplier.routes import admin_suppliers
        
        # تسجيل التطبيقات المستقلة ببادئات الروابط الخاصة بها
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_dashboard, url_prefix='/admin')
        app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')
        
        print("✅ تم تسجيل كافة الأقسام البرمجية بنجاح.")
    except ImportError as e:
        print(f"❌ خطأ حرج في استيراد الأقسام: {e}")

    # 5. بناء جدار قاعدة البيانات (Database Sync)
    with app.app_context():
        try:
            # استيراد النماذج المركزية لضمان تسجيل الجداول في SQLAlchemy
            import apps.models 
            db.create_all()
            print("✅ تم تعميد جداول قاعدة البيانات (Admin & Suppliers) بنجاح.")
        except Exception as e:
            print(f"⚠️ تنبيه: تعذر تحديث هيكل الجداول تلقائياً: {e}")

    return app

# 6. تعريف محرك التحقق من المستخدم لـ Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """
    يقوم باستعادة مستخدم الإدارة من قاعدة البيانات بناءً على المعرف (ID)
    المخزن في جلسة المتصفح (Session).
    """
    from apps.models.admin_db import AdminUser
    try:
        # تحويل user_id إلى int لضمان التوافق مع SQLite/Postgres
        return AdminUser.query.get(int(user_id))
    except Exception:
        return None
