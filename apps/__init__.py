# coding: utf-8
# 🏢 المصنع المركزي للنواة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# إنشاء الكائنات المركزية كنسخ مستقلة لمنع التعارض الدائري
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # تهيئة الإضافات بربطها بالتطبيق الحالي
    db.init_app(app)
    login_manager.init_app(app)
    
    # 🛡️ الحماية السيادية: تحديد المسار الكامل بعد العزل لـ Flask-Login
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    # 🔑 تعريف الـ user_loader لجلب الهوية من PostgreSQL
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # استيراد وتسجيل البلوبرينتس الفرعية بشكل آمن ومباشر
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard_blueprint
    
    # التوجه مباشرة إلى ملف الروابط لحل تعارض الأسماء في add_supplier
    from apps.add_supplier.routes import suppliers_blueprint

    # عزل المسارات برمجياً لضمان عدم التداخل وحماية هيكلية المنصة
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard_blueprint, url_prefix='/admin')
    app.register_blueprint(suppliers_blueprint, url_prefix='/admin/suppliers')

    return app
