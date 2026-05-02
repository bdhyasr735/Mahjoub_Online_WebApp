from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'admin.admin_login'
    login_manager.login_message_category = "info"

    with app.app_context():
        from core.models.user import User
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from admin_panel import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
