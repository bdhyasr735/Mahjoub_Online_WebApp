from flask import Flask
from config import Config
from .models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة قاعدة البيانات مع التطبيق
    db.init_app(app)

    # استدعاء الموديولات (Blueprints) بشكل رشيق
    with app.app_context():
        # استدعاء لوحة الإدارة
        from admin_panel.routes import admin_bp
        
        # تسجيل الموديول في النظام
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # ملاحظة: سنفعل لوحة المورد (supplier_bp) في الخطوة القادمة
        # from supplier_panel.routes import supplier_bp
        # app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # إنشاء الجداول تلقائياً (المحافظ، الموردين، المنتجات)
        db.create_all()

    return app
