# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي الموحد (نسخة الفحص الاستباقي للـ 404)

import os
import importlib
from flask import Flask, redirect
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    # 1. إعداد المصنع
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

    # 2. 🛡️ سياسة أمان المحتوى
    Talisman(app, force_https=True, content_security_policy={
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://*"]
    }, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    # 3. الإضافات الأساسية
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل مسارات الإدارة (بشكل صريح ومضمون)
    core_blueprints = [
        ('apps.auth_portal.routes', 'auth_portal', '/auth'),
        ('apps.admin_dashboard.routes', 'admin_dashboard', '/admin'),
        ('apps.wallet.routes', 'wallet_app', '/wallet'),
        ('apps.vault.routes', 'vault_bp', '/vault'),
        ('apps.orders.routes', 'orders_bp', '/orders'),
        ('apps.api.webhooks', 'webhooks_bp', '/api')
    ]

    for module_path, bp_name, prefix in core_blueprints:
        try:
            module = importlib.import_module(module_path)
            app.register_blueprint(getattr(module, bp_name), url_prefix=prefix)
        except Exception as e:
            print(f"🚨 [System] خطأ في تسجيل المسار {bp_name}: {e}")

    # 5. 🚀 ميكانيكية الاكتشاف التلقائي (Auto-Discovery Engine)
    apps_dir = os.path.dirname(__file__)
    ignore_folders = {'models', 'extensions', 'static', 'templates', '__pycache__', 'api', 'auth_portal', 'admin_dashboard', 'wallet', 'vault', 'orders'}
    
    for folder in os.listdir(apps_dir):
        if folder in ignore_folders or not os.path.isdir(os.path.join(apps_dir, folder)):
            continue
            
        registry_path = os.path.join(apps_dir, folder, 'registry.py')
        if os.path.exists(registry_path):
            try:
                module = importlib.import_module(f'apps.{folder}.registry')
                if hasattr(module, 'register_app'):
                    module.register_app(app)
                elif hasattr(module, 'register_module'):
                    module.register_module(app)
                print(f"📦 [Auto-Discovery] تم تحميل: {folder}")
            except Exception as e:
                print(f"⚠️ [Auto-Discovery] فشل تحميل {folder}: {e}")

    # [DEBUG] طباعة المسارات الفعلية المسجلة (لحل الـ 404)
    print("📋 [DEBUG] المسارات المسجلة في السيرفر:")
    for rule in app.url_map.iter_rules():
        print(f"DEBUG: Rule: {rule.rule} -> Endpoint: {rule.endpoint}")

    # 6. التوجيه الأساسي
    @app.route('/')
    def index():
        login_path = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')
        return redirect(f'/auth{login_path}')

    # 7. إعداد البيانات
    with app.app_context():
        try:
            from apps.models.admin_db import AdminUser
            db.create_all()
            if not AdminUser.query.filter_by(username='علي محجوب').first():
                admin = AdminUser(username='علي محجوب', role='Owner', phone_number='779077746')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
        except Exception as e:
            print(f"⚠️ [Database Setup] خطأ: {e}")

    return app
