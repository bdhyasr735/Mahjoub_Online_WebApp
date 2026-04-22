import os
from flask import Flask, render_template
from config import Config
from core.models import db
from jinja2 import ChoiceLoader, FileSystemLoader

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. تهيئة قاعدة البيانات
    db.init_app(app)

    # 2. إجبار Flask على البحث في كل مجلدات الـ templates
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join(os.getcwd(), 'templates')),
        FileSystemLoader(os.path.join(os.getcwd(), 'admin_panel/templates')),
        FileSystemLoader(os.path.join(os.getcwd(), 'supplier_panel/templates')),
    ])

    # 3. تسجيل البوابات
    from admin_panel.routes import admin_bp
    from supplier_panel.routes import supplier_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(supplier_bp)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database error: {e}")

    @app.route('/')
    def index():
        return render_template('login.html')

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
