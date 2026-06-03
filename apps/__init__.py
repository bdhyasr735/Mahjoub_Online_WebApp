# coding: utf-8
# 📂 apps/__init__.py - المصنع المحصن والمحمي (نسخة A+ Security)

import os
from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # إعداد الـ Proxy للعمل على Render بسلاسة
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # تهيئة قاعدة البيانات بأمان
        try:
            from apps.models.admin_db import AdminUser
            db.create_all()
        except Exception as e:
            print(f"❌ [Database Error]: {e}")

        @login_manager.user_loader
        def load_user(user_id):
            from apps.models.admin_db import AdminUser
            try: return AdminUser.query.get(int(user_id))
            except: return None

        # 🛡️ التسجيل الدفاعي (Defensive Registration)
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
                print(f"✅ تم تسجيل {bp_name} بنجاح.")
            except Exception as e:
                print(f"⚠️ تحذير: فشل تسجيل {bp_name}، السيرفر سيستمر بالعمل. الخطأ: {e}")

        # 4. توجيه المسارات الأمنية (الخداع الاستراتيجي)
        @app.route('/')
        def root_redirect():
            return redirect('/login')

        @app.route('/robots.txt')
        def robots_txt():
            return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

        # 🛡️ الحماية الأمنية المتقدمة (Security Headers لتقييم A+)
        @app.after_request
        def add_security_headers(response):
            # Strict Transport Security (HSTS)
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            # Content Security Policy (CSP)
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            # Permissions Policy
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            # الحماية التقليدية
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive, nosnippet, noimageindex"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            return response

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
