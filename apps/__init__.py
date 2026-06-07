# coding: utf-8
# 📂 apps/__init__.py - المصنع النهائي المحصن (Render-Ready & Gunicorn-Compatible)

import os
import sys
from flask import Flask, redirect

# جعل مجلد الجذر مرئياً لضمان استيراد الملفات بشكل صحيح
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from apps.extensions import db, login_manager, migrate
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    # 1. إنشاء التطبيق مع تحديد مجلد القوالب الافتراضي
    app = Flask(__name__, template_folder='templates')
    
    # 2. توسيع نطاق بحث Jinja2 ليجد القوالب في مسار الـ auth_portal المخصص
    # هذا يحل مشكلة TemplateNotFound دون الحاجة لنقل الملفات
    app.jinja_loader.searchpath.append(os.path.join(base_dir, 'apps', 'auth_portal', 'templates'))
    
    # 3. إعدادات الأمان والبيانات (تستخدم متغيرات البيئة للإنتاج)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-sovereign-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mahjoub_online.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 4. إعدادات البروكسي (ضروري لتعامل Flask مع HTTPS على Render)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # تسجيل النماذج (Models) لضمان معرفة SQLAlchemy بها
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.vault_db import AdminVault, VaultTransaction
        
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # 5. تسجيل الـ Blueprints يدوياً لضمان الاستقرار التام وتجنب أخطاء الاستيراد
        from apps.auth_portal.routes import auth_portal
        from apps.add_supplier.routes import add_supplier_bp
        from apps.financial_ops.routes import financial_blueprint
        from apps.admin_dashboard.routes import admin_dashboard
        from apps.api.search import api_search
        from apps.wallet.routes import wallet_app

        app.register_blueprint(auth_portal, url_prefix='')
        app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
        app.register_blueprint(financial_blueprint, url_prefix='/financial_ops')
        app.register_blueprint(admin_dashboard, url_prefix='/admin')
        app.register_blueprint(api_search, url_prefix='/api')
        app.register_blueprint(wallet_app, url_prefix='/wallet')

        # 6. مسارات النظام الأساسية
        @app.route('/health')
        def health_check():
            return "OK", 200

        @app.route('/')
        def root_redirect():
            return redirect('/m7jb_sovereign_hq_v2_99x')

        # 7. إضافة ترويسات الأمان لمنع هجمات XSS و Clickjacking
        @app.after_request
        def add_security_headers(response):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            return response

    return app
