import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# 1. تعريف الكائنات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

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

    # 4. إعدادات الدخول
    login_manager.login_view = 'admin_panel.admin_login'
    
    # --- ⚓ المسار الافتراضي (لحل مشكلة عدم ظهور الصفحة) ⚓ ---
    @app.route('/')
    def index():
        # توجيه تلقائي لصفحة دخول الإدارة عند فتح الموقع
        return redirect(url_for('admin_panel.admin_login'))

    with app.app_context():
        # 5. استيراد الموديلات
        from core.models.user import User
        from core.models.product import Product
        from core.models.supplier import Supplier
        
        # ⚠️ ملاحظة: سطر db.drop_all() يُحذف بعد أول تشغيل ناجح
        # db.create_all() 

        # 6. تسجيل البوابات بدقة
        try:
            from supplier_panel.routes import supplier_bp
            if 'supplier_panel' not in app.blueprints:
                app.register_blueprint(supplier_bp, url_prefix='/supplier')
            print("✅ بوابة الموردين نشطة")
        except Exception as e:
            print(f"⚠️ خطأ بوابة الموردين: {e}")

        try:
            from admin_panel.routes import admin_bp 
            if 'admin_panel' not in app.blueprints:
                app.register_blueprint(admin_bp, url_prefix='/admin')
            print("✅ برج الرقابة نشط")
        except Exception as e:
            print(f"⚠️ خطأ بوابة الإدارة: {e}")

        # 7. التعميد (يبقى كما هو للتأكد من وجود الحسابات)
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
