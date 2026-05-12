import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# تعريف قاعدة البيانات عالمياً لسهولة الوصول
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # إعدادات قاعدة البيانات والأمان
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'MAHJOUB_2026_SOVEREIGN'

    db.init_app(app)

    # تسجيل بوابات النظام (Blueprints)
    from apps.admin_portal.routes import admin_bp
    from apps.supplier_portal.routes import supplier_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(supplier_bp)

    @app.route('/')
    def index():
        return """
        <body style='background:#0A0A0A; color:#D4AF37; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'>
            <div style='text-align:center; border:2px solid #3D0066; padding:40px; border-radius:15px; box-shadow: 0 0 20px #3D0066;'>
                <h1>🛡️ منصة محجوب أونلاين السيادية</h1>
                <p style='color:white;'>الهيكل الجديد يعمل بنجاح</p>
                <a href='/admin/dashboard' style='color:#D4AF37; text-decoration:none; margin:10px; display:inline-block;'>[ بوابة الإدارة ]</a>
                <a href='/supplier/dashboard' style='color:#3D0066; text-decoration:none; margin:10px; display:inline-block;'>[ بوابة الموردين ]</a>
            </div>
        </body>
        """

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
