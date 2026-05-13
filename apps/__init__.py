from flask import Flask
import os

def create_app():
    # إنشاء التطبيق وتحديد مسار الملفات الثابتة العامة
    app = Flask(__name__)
    
    # إعدادات الحماية والتشفير للمنصة
    app.config['SECRET_KEY'] = 'mahjoub_online_2026_key'
    
    # تسجيل المحركات (Blueprints)
    
    # 1. محرك بوابة التحقق
    from .auth_portal.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 2. محرك إدارة الموردين
    from .add_supplier.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/suppliers')

    # 3. محرك لوحة التحكم الإدارية
    from .admin_dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/admin')

    return app
