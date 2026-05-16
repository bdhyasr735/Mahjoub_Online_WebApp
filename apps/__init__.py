# coding: utf-8
# 🛡️ المحرك المركزي لمنصة محجوب أونلاين 2026
# التوثيق: المصنع الرئيسي (App Factory) وإدارة السيادة الرقمية

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash # استيراد مشفر كلمة السر

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

    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه المنطقة السيادية."
    login_manager.login_message_category = "info"

    # 4. تسجيل الأقسام البرمجية (Blueprints)
    try:
        from apps.auth_portal.routes import auth_bp
        from apps.admin_dashboard.routes import admin_dashboard
        
        # التعديل الحاسم والمصحح: استيراد البلوبرينت مباشرة من حزمة القسم لمنع انكسار محرك جينجا والتداخل
        from apps.add_supplier import admin_suppliers
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_dashboard, url_prefix='/admin')
        app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers')
        
        print("✅ تم تسجيل كافة الأقسام البرمجية بنجاح.")
    except ImportError as e:
        print(f"❌ خطأ حرج في استيراد الأقسام: {e}")

    # 5. بناء جدار قاعدة البيانات وزرع حساب المالك (Sovereignty Seed)
    with app.app_context():
        try:
            import apps.models 
            db.create_all()
            
            # --- 🛡️ إجراءات تعميد المالك في قاعدة البيانات (الإصدار المصحح) ---
            from apps.models.admin_db import AdminUser
            
            # البحث عن "علي محجوب" في جدول الإدارة
            owner = AdminUser.query.filter_by(username='علي محجوب').first()
            
            if not owner:
                print("🚀 جاري زرع حساب المالك السيادي بكافة الحقول الإجبارية...")
                new_owner = AdminUser(
                    full_name='علي محجوب',          # حل مشكلة NotNull
                    username='علي محجوب',
                    email='admin@mahjoub.online',   # حل مشكلة NotNull
                    password_hash=generate_password_hash('123'),
                    role='Owner'
                )
                db.session.add(new_owner)
                db.session.commit()
                print("✅ [سيادة] تم تعميد 'علي محجوب' مالكاً رسمياً للمنصة.")
            else:
                # تحديث البيانات الحيوية لضمان المطابقة
                owner.full_name = 'علي محجوب'
                owner.password_hash = generate_password_hash('123')
                db.session.commit()
                print(f"📡 نظام الحوكمة مفعل: المالك '{owner.username}' في وضع الاستعداد.")
            # ---------------------------------------------
            
            print("✅ تم تعميد جداول قاعدة البيانات بنجاح.")
        except Exception as e:
            # طباعة الخطأ بشكل مفصل للمساعدة في التشخيص
            print(f"⚠️ تنبيه: خطأ أثناء تهيئة قاعدة البيانات: {e}")

    return app

# 6. تعريف محرك التحقق من المستخدم لـ Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from apps.models.admin_db import AdminUser
    try:
        return AdminUser.query.get(int(user_id))
    except Exception:
        return None
