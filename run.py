import os
from flask import Flask, render_template
from config import Config
from core.models import db

def create_app():
    # نحدد هنا أن المجلد الرئيسي للقوالب هو 'templates'
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)

    # استيراد البلوبرنت داخل الدالة لتجنب مشاكل المسارات
    from admin_panel.routes import admin_bp
    from supplier_panel.routes import supplier_bp
    
    # تسجيل البوابات
    app.register_blueprint(admin_bp)
    app.register_blueprint(supplier_bp)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database connection error: {e}")

    @app.route('/')
    def index():
        return render_template('login.html')

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
