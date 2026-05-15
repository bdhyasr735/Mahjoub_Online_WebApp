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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_key_2026')
    
    # معالجة رابط قاعدة البيانات ليتوافق مع معايير Railway الحديثة
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تحسين الأداء: منع السيرفر من "التعليق" أثناء الاستعلامات الطويلة
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

    # 4. تسجيل الأقسام البرمجية (Blueprints)
    # الاستيراد هنا يحل مشكلة التبعيات الدائرية
    from apps.auth_portal.routes import auth_bp
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')

    # 5. بناء جدار قاعدة البيانات (Database Sync)
    with app.app_context():
        try:
            # استيراد النماذج من الحزمة المركزية
            import apps.models 
            db.create_all()
            print("✅ تم تعميد جداول قاعدة البيانات بنجاح.")
        except Exception as e:
            print(f"⚠️ تنبيه: السيرفر يعمل ولكن تعذر تحديث الجداول تلقائياً: {e}")

    return app

# تعريف مستخدم النظام لـ Flask-Login (مطلوب لعمل login_required)
@login_manager.user_loader
def load_user(user_id):
    from apps.models.admin_db import AdminUser
    return AdminUser.query.get(int(user_id))
