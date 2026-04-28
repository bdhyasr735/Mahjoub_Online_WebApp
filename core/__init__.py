import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

# 1. تعريف الكائنات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # حل مشكلة الروابط في بيئة Render/Railway
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # 2. الإعدادات
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///mahjoub_online.db'
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'mahjoub-secret-key-123'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. التهيئة
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 4. إعدادات الدخول الافتراضية
    login_manager.login_view = 'admin_panel.admin_login'

    # --- ⚓ الموجه المركزي (لحل مشكلة عدم ظهور البوابات) ⚓ ---
    @app.route('/')
    def index():
        # عند فتح الرابط الرئيسي، يوجهنا للنظام تلقائياً
        return redirect(url_for('admin_panel.admin_login'))

    with app.app_context():
        # 5. استيراد الموديلات
        from core.models.user import User
        
        # إنشاء الجداول (بدون مسح القديم لضمان استمرار البيانات)
        db.create_all() 

        # 6. تسجيل بوابة الموردين (التي أرفقت كودها)
        try:
            from supplier_panel.routes import supplier_bp
            if 'supplier_panel' not in app.blueprints:
                app.register_blueprint(supplier_bp, url_prefix='/supplier')
            print("✅ بوابة الموردين مفعلة على مسار /supplier")
        except Exception as e:
            print(f"❌ خطأ في ربط بوابة الموردين: {e}")

        # 7. تسجيل بوابة الإدارة
        try:
            from admin_panel.routes import admin_bp 
            if 'admin_panel' not in app.blueprints:
                app.register_blueprint(admin_bp, url_prefix='/admin')
            print("✅ برج الرقابة مفعل على مسار /admin")
        except Exception as e:
            print(f"❌ خطأ في ربط بوابة الإدارة: {e}")

        # 8. التعميد السيادي (التأكد من وجود المستخدمين)
        try:
            if not User.query.filter_by(username="علي محجوب").first():
                admin_user = User(username="علي محجوب", role="admin", status="approved")
                admin_user.set_password("123")
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            db.session.rollback()

    return app

@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    return db.session.get(User, int(user_id))
