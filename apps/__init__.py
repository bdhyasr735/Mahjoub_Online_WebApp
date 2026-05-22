# apps/__init__.py

from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from apps.models.admin_db import AdminUser  # تأكد من استيراد موديل المسؤول

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    
    # تحديد صفحة تسجيل الدخول التي سيتم توجيه المستخدم غير المصرح له إليها
    login_manager.login_view = 'auth_portal.login' 

    # --- هذا هو الجزء المفقود الذي يسبب الانهيار ---
    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))
    # ----------------------------------------------

    # تسجيل الـ Blueprints
    from apps.admin_dashboard import admin_dashboard_bp
    from apps.add_supplier import admin_suppliers_bp
    from apps.auth_portal import auth_portal_bp
    
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(auth_portal_bp, url_prefix='/auth')

    return app
