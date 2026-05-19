# coding: utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # استيراد النماذج (تم تصحيح الاستيراد لمنع الدائري)
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import Wallet
        db.create_all()

    login_manager.login_view = 'auth_portal.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # استيراد البلوبرينتس
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # تسجيل البلوبرينتس مع تحديد الأسماء (Names) لتطابق ما في الـ HTML والـ Routes
    app.register_blueprint(auth_blueprint, url_prefix='/auth', name='auth_portal')
    app.register_blueprint(admin_dashboard, url_prefix='/admin', name='admin_dashboard')
    
    # هنا تم ربط البلوبرينت بالاسم 'add_supplier' كما هو معرف في routes.py
    app.register_blueprint(admin_suppliers_bp, url_prefix='/admin', name='add_supplier')
    
    app.register_blueprint(admin_wallet, url_prefix='/admin', name='admin_wallet')

    # طباعة تأكيدية في السجلات (اختياري للـ Debugging)
    print("✅ تم ربط محرك الموردين بالاسم: add_supplier")

    return app
