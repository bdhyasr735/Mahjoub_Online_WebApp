# coding: utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# إنشاء الكائنات المركزية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)

    # 🛑 استيراد النماذج داخل سياق التطبيق لمنع الاستيراد الدائري
    with app.app_context():
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import Wallet
        db.create_all()

    # 🛡️ إعدادات الحماية
    login_manager.login_view = 'auth_portal.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # ⚙️ استيراد البلوبرينتس
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # 🚀 تسجيل البلوبرينتس مع تحديد اسم (name) يطابق توقعات النظام في الـ HTML
    # هذا هو سر حل خطأ 'Could not build url'
    app.register_blueprint(auth_blueprint, url_prefix='/auth', name='auth_portal')
    app.register_blueprint(admin_dashboard, url_prefix='/admin', name='admin_dashboard')
    
    # هنا الحيلة: نجعل النظام يرى الموردين باسم 'admin_suppliers' كما يبحث عنه في سجلاتك
    app.register_blueprint(admin_suppliers_bp, url_prefix='/admin', name='admin_suppliers')
    
    app.register_blueprint(admin_wallet, url_prefix='/admin', name='admin_wallet')

    return app
