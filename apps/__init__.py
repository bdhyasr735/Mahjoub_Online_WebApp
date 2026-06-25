# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي الموحد

import os
import importlib
from flask import Flask, redirect, url_for
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static', 
                static_url_path='/static',
                instance_relative_config=True)
    
    app.config.from_object(Config)

    # تحسينات الأمان
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True
    )

    # 🛡️ سياسة أمان المحتوى
    Talisman(app, force_https=True, content_security_policy={
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://*"]
    }, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    # الإضافات الأساسية
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # تسجيل المسارات
    with app.app_context():
        # 1. التسجيل اليدوي للمكونات الأساسية (لضمان الاستقرار)
        try:
            from apps.auth_portal.routes import auth_portal
            from apps.admin_dashboard.routes import admin_dashboard
            from apps.wallet.routes import wallet_app
            from apps.vault.routes import vault_bp
            from apps.orders.routes import orders_bp
            from apps.api.webhooks import webhooks_bp

            app.register_blueprint(auth_portal, url_prefix='/auth')
            app.register_blueprint(admin_dashboard, url_prefix='/admin')
            app.register_blueprint(wallet_app, url_prefix='/wallet')
            app.register_blueprint(vault_bp, url_prefix='/vault')
            app.register_blueprint(orders_bp, url_prefix='/orders')
            app.register_blueprint(webhooks_bp, url_prefix='/api')
        except Exception as e:
            print(f"❌ [CRITICAL] خطأ في تسجيل المسارات الأساسية: {e}")
            raise

        # 2. التسجيل الديناميكي لموديولات الموردين (System Registry)
        # هذا الجزء يبحث في مجلد 'apps' عن أي موديول يبدأ بـ 'suppliers_'
        # ويسجل ملف الـ registry.py الخاص به تلقائياً.
        suppliers_dir = os.path.join(app.root_path, 'apps')
        for folder in os.listdir(suppliers_dir):
            if folder.startswith('suppliers_'):
                registry_path = os.path.join(suppliers_dir, folder, 'registry.py')
                if os.path.exists(registry_path):
                    try:
                        module_name = f"apps.{folder}.registry"
                        module = importlib.import_module(module_name)
                        if hasattr(module, 'register_module'):
                            module.register_module(app)
                    except Exception as e:
                        print(f"⚠️ [Registry] تعذر تسجيل موديول الموردين {folder}: {e}")

    @app.route('/')
    def index():
        return redirect(url_for('auth_portal.login'))

    # إعداد البيانات (Seeding)
    # [بقية كود الزرع كما هو لا تغيير عليه]
    with app.app_context():
        db.create_all()
        # (كود زرع المسؤول والمورد...)
        
    return app
