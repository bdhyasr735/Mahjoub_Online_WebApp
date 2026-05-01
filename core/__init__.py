from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# تعريف الإضافات
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # تحديد الصفحة التي يتم تحويل غير المسجلين إليها
    login_manager.login_view = 'admin.admin_login'
    login_manager.login_message_category = 'info'

    # --- هذا الجزء هو الحل للخطأ الحالي ---
    from core.models.user import User  # استيراد موديل المستخدم
    
    @login_manager.user_loader
    def load_user(user_id):
        # البحث عن المستخدم بواسطة المعرف (ID) لتمكينه من دخول الإدارة
        return User.query.get(int(user_id))
    # -------------------------------------

    with app.app_context():
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        @app.route('/')
        def index():
            # تحويل تلقائي للوحة تحكم الإدارة لتركيز العمل هناك
            return redirect(url_for('admin.admin_login'))

        return app
