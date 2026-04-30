import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # --- إعدادات قاعدة البيانات والأمان ---
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "Mahjoub_Smart_Market_2026")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ==========================================
    # مكان الإضافة الجديد (لضمان بقاء الجلسة نشطة وآمنة)
    # ==========================================
    app.config['SESSION_COOKIE_SECURE'] = True    # لضمان عمل الجلسة عبر رابط Railway الآمن (HTTPS)
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # لمنع الوصول للجلسة عبر السكربتات الخبيثة
    app.config['REMEMBER_COOKIE_DURATION'] = 2592000 # بقاء الدخول نشطاً لـ 30 يوماً
    # ==========================================

    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'supplier_panel.supplier_login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى هذه الصفحة."
    login_manager.login_message_category = "info"

    with app.app_context():
        # تسجيل البوابات
        from admin_panel.routes import admin_bp
        from supplier_panel.routes import supplier_bp
        
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        from core.models.user import User

    return app

@login_manager.user_loader
def load_user(user_id):
    from core.models.user import User
    return User.query.get(int(user_id))
