import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# تهيئة المكتبات الأساسية (db و login_manager)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # --- إعدادات قاعدة البيانات (متوافقة تماماً مع Render) ---
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        # تصحيح البروتوكول ليتوافق مع SQLAlchemy الحديثة
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    # مفتاح السري للمنصة (Mahjoub Online 2026)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "Mahjoub_Smart_Market_2026")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- مبادرة المكتبات داخل التطبيق ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد صفحة الدخول الافتراضية عند محاولة الوصول لصفحة محمية بـ @login_required
    # تم ضبطها لتوجه الموردين لصفحة دخولهم كخيار افتراضي
    login_manager.login_view = 'supplier_panel.supplier_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه الصفحة."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- تسجيل البوابات (Blueprints) باستخدام ملفات routes.py الموحدة ---
        
        # 1. تسجيل بوابة الإدارة (Admin Panel)
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        # 2. تسجيل بوابة الموردين (Supplier Panel)
        from supplier_panel.routes import supplier_bp
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # استيراد الموديلات لضمان تعريف الجداول في قاعدة البيانات
        from core.models.user import User

    return app

# --- محمل المستخدم (User Loader) المطلوب لـ Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    # جلب كائن المستخدم من قاعدة البيانات عبر معرفه الرقمي
    return User.query.get(int(user_id))
