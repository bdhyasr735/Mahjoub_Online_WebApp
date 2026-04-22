import os
from flask import Flask
from flask_login import LoginManager
from admin_panel.models import db, User
from admin_panel.admin_routes import admin_bp

app = Flask(__name__) # تعريف app مباشرة في الأعلى لسهولة وصول Gunicorn

# إعدادات الأمان
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mahjoub_2026_key')

# استخدم الرابط الخارجي (External) من ريندر هنا
app.config['SQLALCHEMY_DATABASE_URI'] = "ضع_الرابط_الخارجي_هنا"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(admin_bp, url_prefix='/admin')

with app.app_context():
    try:
        db.create_all()
        print("✅ Database Connected")
    except Exception as e:
        print(f"⚠️ Database connection failed but app is running: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
