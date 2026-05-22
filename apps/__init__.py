# coding: utf-8
from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from apps.models.admin_db import AdminUser

def create_app():
    # 1. إنشاء التطبيق
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2. تهيئة الإضافات (Extensions)
    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد مسار صفحة الدخول التلقائي
    login_manager.login_view = 'auth_portal.login' 

    # 3. تعريف دالة تحميل المستخدم (إصلاح خطأ الانهيار)
    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل الـ Blueprints (نواة نظام النوافذ المستقلة)
    
    # بوابة الدخول
    from apps.auth_portal import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # لوحة القيادة
    from apps.admin_dashboard import admin_dashboard_bp
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    
    # إدارة الموردين
    from apps.add_supplier import admin_suppliers_bp
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    
    # المحفظة المالية
    from apps.wallet import wallet_bp
    app.register_blueprint(wallet_bp, url_prefix='/wallet')

    return app
