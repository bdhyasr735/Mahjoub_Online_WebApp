# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي للنظام (النسخة النهائية)

import os
import importlib
from flask import Flask, redirect, url_for
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    # 1. إعداد المصنع مع جعل مسار القوالب أكثر مرونة
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static', 
                static_url_path='/static',
                instance_relative_config=True)
    
    app.config.from_object(Config)

    # تحسينات التوافق مع بيئة الإنتاج
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # 2. 🛡️ سياسة أمان المحتوى (CSP)
    Talisman(app, force_https=True, content_security_policy={
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://*"]
    }, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    # 3. تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل المسارات الأساسية (Hardcoded Blueprints)
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
        print(f"🚨 [CRITICAL] خطأ في تسجيل المسارات الأساسية: {e}")

    # 5. المحرك التلقائي لاكتشاف التطبيقات (Dynamic Auto-Discovery)
    apps_dir = os.path.dirname(__file__)
    # المجلدات المستثناة التي لها تسجيل يدوي أعلاه
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
            except Exception as e:
                print(f"⚠️ [System] تجاوز خطأ في تحميل التطبيق {folder}: {e}")

    @app.route('/')
    def index():
        return redirect(url_for('auth_portal.login'))

    # 6. إعداد البيانات والجداول
    with app.app_context():
        try:
            from apps.models.admin_db import AdminUser
            db.create_all()
            
            # تأسيس المالك
            owner_username = 'علي محجوب'
            if not AdminUser.query.filter_by(username=owner_username).first():
                admin = AdminUser(username=owner_username, role='Owner', phone_number='779077746')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ [System] تم تأسيس حساب المالك بنجاح.")
        except Exception as e:
            print(f"⚠️ [Error] فشل في تهيئة قاعدة البيانات: {e}")

    return app
