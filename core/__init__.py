from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # رؤوس CORS للسماح بالعمليات المتقاطعة
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'admin.login'
    login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى النظام السيادي."
    login_manager.login_message_category = "info"

    with app.app_context():
        from core.models.user import User
        from core.models.vendor import Vendor
        
        # 🛡️ تصحيح الترسانة: إنشاء الجداول فقط إذا لم تكن موجودة
        # تم تعطيل drop_all لحماية بيانات الموردين من الحذف المتكرر
        try:
            db.create_all() 
        except Exception as e:
            print(f"⚠️ تنبيه: قاعدة البيانات قائمة بالفعل أو واجهت مشكلة: {e}")
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        @app.context_processor
        def utility_processor():
            def get_next_vendor_id():
                try:
                    # منطق جلب المعرف السيادي التالي (MAH-9631)
                    last_vendor = Vendor.query.order_by(Vendor.id.desc()).first()
                    if last_vendor and last_vendor.e_wallet and '-' in last_vendor.e_wallet:
                        parts = last_vendor.e_wallet.split('-')
                        if len(parts) > 1:
                            return f"MAH-{int(parts[1]) + 1}"
                    return "MAH-9631"
                except:
                    return "MAH-9631"
            return dict(next_id=get_next_vendor_id())

        from admin_panel.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
