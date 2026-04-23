from flask import Flask
from config import Config
from .models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. تهيئة قاعدة البيانات (PostgreSQL) مع التطبيق
    db.init_app(app)

    # 2. تشغيل سياق التطبيق لتسجيل الموديولات وتأسيس الجداول
    with app.app_context():
        
        # --- استدعاء الموديولات (Blueprints) بشكل رشيق ---
        
        # استدعاء وتسجيل لوحة الإدارة (Admin Panel)
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # استدعاء وتسجيل بوابة الموردين (Supplier Panel)
        from supplier_panel.routes import supplier_bp
        app.register_blueprint(supplier_bp, url_prefix='/supplier')

        # 3. إنشاء الجداول تلقائياً إذا لم تكن موجودة (المحافظ، الموردين، المنتجات)
        # سيتم تنفيذ الفهرسة (Indexing) التي صممناها في models.py هنا
        db.create_all()

    return app
