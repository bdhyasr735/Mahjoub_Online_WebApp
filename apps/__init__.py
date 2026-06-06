# -*- coding: utf-8 -*-
# 📂 apps/__init__.py - المصنع الاحترافي والمحصن (النسخة النهائية المصححة)

import os
from datetime import timedelta
from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager, migrate

# 🛡️ دالة تسجيل آمنة للـ Blueprints الديناميكية
def safe_register(app_instance, module_path, attr_name, prefix):
    try:
        module = __import__(module_path, fromlist=[attr_name])
        blueprint = getattr(module, attr_name)
        app_instance.register_blueprint(blueprint, url_prefix=prefix)
        print(f"✅ Registered: {module_path}")
    except Exception as e:
        print(f"⚠️ Security Alert: Failed to register {attr_name} - Error: {e}")

def create_app():
    # 1. إنشاء التطبيق
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2. إعدادات الأمان
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.config['SESSION_COOKIE_HTTPONLY'] = True  
    app.config['SESSION_COOKIE_SECURE'] = True    
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # 3. إعدادات الوكيل لضمان عمل HTTPS على Render
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # 4. تهيئة الامتدادات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # 5. استيراد النماذج لضمان تهيئتها (تجنب الحلقات)
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.vault_db import AdminVault, VaultTransaction
        
        # 6. المزامنة التلقائية للجداول
        try:
            db.create_all()  
        except Exception as e:
            print(f"⚠️ Synchronization issue: {e}")

        # 7. تحميل المستخدم
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # 8. تسجيل المسارات (Blueprints) باستخدام المسارات المباشرة لضمان الاستقرار
        safe_register(app, 'apps.auth_portal.routes', 'auth_portal', '')
        safe_register(app, 'apps.add_supplier.routes', 'add_supplier_bp', '/suppliers')
        safe_register(app, 'apps.financial_ops.routes', 'financial_blueprint', '/financial_ops')
        safe_register(app, 'apps.admin_dashboard.routes', 'admin_dashboard', '/admin')
        safe_register(app, 'apps.api.search', 'api_search', '/api')
        
        # تسجيل المحفظة بشكل صريح لضمان تطابق الـ Endpoint
        try:
            from apps.wallet.routes import wallet_app
            app.register_blueprint(wallet_app, url_prefix='/wallet')
            print("✅ Registered: apps.wallet.routes")
        except Exception as e:
            print(f"⚠️ Error registering wallet_app: {e}")

        # 9. المسارات العامة
        @app.route('/robots.txt')
        def robots_txt():
            return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

        @app.route('/')
        def root_redirect():
            return redirect('/login')

        # 10. ترويسات الأمان (Security Headers)
        @app.after_request
        def add_security_headers(response):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' https://cdn.qumra.cloud; frame-ancestors 'none';"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers.pop("Server", None)
            return response

    return app

# تعيين نقطة الدخول (Entry Point) التي سيستخدمها Gunicorn
app = create_app()
