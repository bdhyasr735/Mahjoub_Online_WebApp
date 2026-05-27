# coding: utf-8
# 🏗️ مصنع التطبيق المركزي (Application Factory) - منصة محجوب أونلاين 2026
import os
from flask import Flask
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.utils.security import AESCipher # استيراد المشفر

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # تهيئة المشفر وربطه بـ app
    app.cipher = AESCipher(app.config.get('ENCRYPTION_KEY', os.getenv('ENCRYPTION_KEY')))
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    from apps.extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    with app.app_context():
        # 1. استيراد الموديلات داخل سياق التطبيق
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.settlements_db import AdminSettlement
        from apps.models.statement_db import SupplierStatement 
        
        # 2. إنشاء الجداول
        db.create_all() 
        
        # 3. دالة تحميل المستخدم يجب أن تكون داخل السياق
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # 4. تسجيل البلوبرينتس
        from apps.auth_portal.routes import auth_blueprint
        from apps.admin_dashboard.routes import admin_dashboard
        from apps.add_supplier.routes import admin_suppliers_bp
        from apps.financial_ops.routes import financial_blueprint 
        from apps.statement import statement_blueprint

        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(admin_dashboard)
        app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
        app.register_blueprint(financial_blueprint, url_prefix='/finance')
        app.register_blueprint(statement_blueprint, url_prefix='/statement')

    return app

app = create_app()
