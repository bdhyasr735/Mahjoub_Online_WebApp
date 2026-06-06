# coding: utf-8
import os
import sys
from datetime import timedelta
from flask import Flask, redirect, render_template # أضفنا render_template

# إضافة المجلد الجذر إلى مسار النظام
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager, migrate

def safe_register(app_instance, module_path, attr_name, prefix):
    try:
        module = __import__(module_path, fromlist=[attr_name])
        blueprint = getattr(module, attr_name)
        app_instance.register_blueprint(blueprint, url_prefix=prefix)
    except Exception as e:
        print(f"⚠️ Critical: Failed to register {attr_name} - {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # إعدادات الأمان
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_HTTPONLY'] = True  
    app.config['SESSION_COOKIE_SECURE'] = True    
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # استقرار الاتصال
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # استيراد النماذج
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.vault_db import AdminVault, VaultTransaction
        
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # تسجيل المسارات
        safe_register(app, 'apps.auth_portal.routes', 'auth_portal', '')
        safe_register(app, 'apps.add_supplier.routes', 'add_supplier_bp', '/suppliers')
        safe_register(app, 'apps.financial_ops.routes', 'financial_blueprint', '/financial_ops')
        safe_register(app, 'apps.admin_dashboard.routes', 'admin_dashboard', '/admin')
        safe_register(app, 'apps.api.search', 'api_search', '/api')
        safe_register(app, 'apps.wallet.routes', 'wallet_app', '/wallet')

        # --- "حاوية الحماية" لمنع توقف السيرفر بالكامل عند حدوث أي خطأ ---
        @app.errorhandler(Exception)
        def handle_exception(e):
            print(f"🚨 Global Error Caught: {e}")
            return "عذراً، حدث خطأ مؤقت. النظام لا يزال يعمل.", 500

        @app.route('/health')
        def health_check():
            return "System is Online", 200

        @app.route('/')
        def root_redirect():
            return redirect('/login')

        @app.after_request
        def add_security_headers(response):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            return response

    return app
