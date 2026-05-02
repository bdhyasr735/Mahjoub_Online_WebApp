from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

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

    from core.models.user import User 
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        try:
            # --- الإجراء الحاسم: تصفير شامل للبيانات والجداول ---
            print("🚨 جاري تصفير قاعدة البيانات وإعادة التهيئة...")
            db.drop_all() 
            db.create_all() 
            print("✅ تم إعادة بناء الجداول بنجاح.")

            # --- زرع حساب القائد علي محجوب ---
            admin_user = User(
                username="علي محجوب", 
                role='admin', 
                is_active_account=True
            )
            admin_user.set_password('123')
            db.session.add(admin_user)
            db.session.commit()
            print("👑 تم زرع حساب القائد بنجاح: علي محجوب / 123")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ أثناء التصفير أو الزرع: {e}")

        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
