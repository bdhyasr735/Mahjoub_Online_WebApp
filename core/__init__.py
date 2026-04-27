import os
import sys
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # تثبيت مسار المشروع لضمان رؤية المجلدات المجاورة
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(project_root, '..')))

    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'supplier_panel.login'

    with app.app_context():
        # استيراد الموديلات من المجلد المخصص لها
        from core.models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # ربط البوابات (التعميد السيادي)
        try:
            from admin_panel import admin_bp
            from supplier_panel import supplier_bp
            
            app.register_blueprint(admin_bp, url_prefix='/admin')
            app.register_blueprint(supplier_bp, url_prefix='/supplier')
            print("✅ [System] تم ربط بوابات الإدارة والموردين.")
        except Exception as e:
            print(f"❌ [Critical Error] فشل الربط: {e}")

    return app
