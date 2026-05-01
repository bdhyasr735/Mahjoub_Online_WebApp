from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from sqlalchemy import text

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'admin.admin_login'
    login_manager.login_message_category = 'info'

    from core.models.user import User 
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # --- منطق الترميم التلقائي الشامل لقاعدة البيانات (نسخة علي محجوب السيادية) ---
        try:
            # 1. فحص وترميم الأعمدة الأساسية فقط لضمان عمل "محجوب أونلاين"
            # تم حذف عمود الـ email نهائياً تماشياً مع طلبك
            db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(150) UNIQUE;'))
            db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);'))
            db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT \'admin\';'))
            db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active_account BOOLEAN DEFAULT TRUE;'))
            
            db.session.commit()
            print("✅ تم فحص وترميم أعمدة قاعدة البيانات بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ تنبيه: قاعدة البيانات محدثة أو هناك تداخل بسيط: {e}")
        # --------------------------------------------------

        # تسجيل Blueprints (التأكد من الربط الصحيح بالمسارات)
        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

        @app.route('/')
        def index():
            return redirect(url_for('admin.admin_login'))

    return app
