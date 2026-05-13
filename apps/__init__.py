from flask import Flask
import os
from models.supplier_db import db  # استيراد قاعدة البيانات الموحدة

def create_app():
    app = Flask(__name__)
    
    # الإعدادات السيادية للربط مع Railway
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'mahjoub_online_2026_key'
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mahjoub_admin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # تسجيل المحركات (Blueprints) بمسارات منفصلة:

    # 1. بوابة التحقق
    from .auth_portal.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 2. لوحة التحكم المركزية (Admin Dashboard)
    # هذا المحرك سيتولى مسار /admin الأساسي
    from .admin_dashboard.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 3. إدارة الموردين (Add Supplier)
    # لتجنب التعارض، نغير الـ prefix هنا
    from .add_supplier.routes import admin_suppliers
    app.register_blueprint(admin_suppliers, url_prefix='/admin/suppliers-portal')

    return app
