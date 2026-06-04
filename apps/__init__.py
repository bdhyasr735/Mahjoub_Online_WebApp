# coding: utf-8
# 📂 apps/__init__.py - المصنع المحصن والمحمي (Security Hardened & Session Secured)

import os
from datetime import timedelta
from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 🛡️ إعدادات الأمان للجلسات (Session Security)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # حماية ضد سرقة الجلسة (XSS)
    app.config['SESSION_COOKIE_SECURE'] = True    # فرض الاتصال الآمن (HTTPS فقط)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # 🛡️ الحماية من التزييف (ProxyFix لضمان صحة عناوين الـ IP)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # 🛡️ إعدادات قاعدة البيانات الدفاعية
        try:
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            from apps.models.statement_db import SupplierStatement
            from apps.models.settlements_db import AdminSettlement
            db.create_all() 
        except Exception as e:
            print(f"❌ [Security DB Error]: {e}")

        @login_manager.user_loader
        def load_user(user_id):
            from apps.models.admin_db import AdminUser
            try: return AdminUser.query.get(int(user_id))
            except: return None

        # 🛡️ تسجيل دفاعي صارم
        blueprints_map = [
            ('apps.auth_portal.routes', 'auth_portal', ''),
            ('apps.add_supplier.routes', 'add_supplier', '/suppliers'),
            ('apps.financial_ops.routes', 'financial_blueprint', '/financial_ops'),
            ('apps.statement.routes', 'statement_blueprint', '/statement'),
            ('apps.admin_dashboard.routes', 'admin_dashboard', '/admin'),
            ('api.webhook', 'webhook_bp', '')
        ]

        for module_path, bp_name, prefix in blueprints_map:
            try:
                module = __import__(module_path, fromlist=[bp_name])
                app.register_blueprint(getattr(module, bp_name), url_prefix=prefix)
            except Exception as e:
                print(f"⚠️ Security Alert: Failed to register {bp_name}")

        # 🛡️ حظر الزحف والأرشفة جذرياً
        @app.route('/robots.txt')
        def robots_txt():
            return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

        @app.route('/')
        def root_redirect():
            return redirect('/login')

        # 🛡️ الحماية المتقدمة (Security Headers مع التعديل اللازم لعمل التصميم)
        @app.after_request
        def add_security_headers(response):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                # تم إضافة cdn.jsdelivr.net و cdnjs.cloudflare.com للسماح بالتنسيق
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' https://cdn.qumra.cloud; "
                "frame-ancestors 'none';"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive, nosnippet, noimageindex"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
            response.headers.pop("Server", None)
            return response

    return app

app = create_app()
