# apps/__init__.py
from flask import Flask
from apps.extensions import db, login_manager
from config import Config
from apps.models.admin_db import AdminUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    
    # تعيين مسار صفحة الدخول (يجب أن يطابق اسم الـ route في routes.py)
    login_manager.login_view = 'auth_portal.login' 

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # تسجيل الـ Blueprint الخاص ببوابة الدخول
    from apps.auth_portal import auth_portal_bp
    app.register_blueprint(auth_portal_bp, url_prefix='/auth')

    # تسجيل باقي الـ Blueprints...
    return app
