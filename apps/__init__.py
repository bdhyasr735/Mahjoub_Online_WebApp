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
    
    # تحديد مسار بوابة النفاذ لـ Flask-Login ونوع التنبيه
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    # 🔑 الحارس السيادي: تعريف الـ user_loader لجلب الهوية من PostgreSQL
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # تسجيل البلوبرينتس الفرعية بشكل معزول ومحمي
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard_blueprint
    from apps.add_supplier import suppliers_blueprint

    app.register_blueprint(auth_blueprint, url_for_security='auth_portal')
    app.register_blueprint(admin_dashboard_blueprint, url_for_security='admin_dashboard')
    app.register_blueprint(suppliers_blueprint, url_for_security='admin_suppliers')

    return app
