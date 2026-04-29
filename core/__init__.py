import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# تهيئة المكتبات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # --- إعدادات قاعدة البيانات (متوافقة مع Render) ---
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        # تصحيح بروتوكول SQLAlchemy ليتوافق مع PostgreSQL الحديثة
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "Mahjoub_Smart_Market_2026")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- مبادرة المكتبات داخل التطبيق ---
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد صفحة الدخول الافتراضية (سيتم توجيه غير المسجلين إليها)
    # ملاحظة: يمكنك تغييرها إلى 'supplier_panel.supplier_login' إذا كان أغلب المستخدمين موردين
    login_manager.login_view = 'admin_panel.admin_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه الصفحة."
    login_manager.login_message_category = "info"

    with app.app_context():
        # --- تسجيل البوابات (Blueprints) مع تصحيح المسارات ---
        
        # 1. بوابة الإدارة (Admin Panel)
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        # 2. بوابة الموردين (Supplier Panel)
        from supplier_panel.routes import supplier_bp
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # استيراد الموديلات لضمان إنشاء الجداول (عند الحاجة)
        from core.models import user

    return app

# --- محمل المستخدم (User Loader) لـ Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    # البحث عن المستخدم في قاعدة البيانات عبر المعرف الفريد
    return User.query.get(int(user_id))
