from flask import Flask
from config import Config
from .models import db # استدعاء db من ملف models.py

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة db مع التطبيق
    db.init_app(app)

    with app.app_context():
        # استدعاء وتسجيل المسارات
        from admin_panel.routes import admin_bp
        from supplier_panel.routes import supplier_bp
        
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # إنشاء الجداول في قاعدة البيانات (مثل PostgreSQL على Railway)
        db.create_all()

    return app
