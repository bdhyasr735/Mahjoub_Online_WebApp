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

    # 1. تحسينات أمان ملفات تعريف الارتباط
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True
    )

    # 2. سياسة أمان المحتوى (CSP)
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
        # الاستقلالية: نستخدم استيراداً محلياً لتجنب التداخل عند بدء التشغيل
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل المكونات الأساسية
    with app.app_context():
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

        # 5. التسجيل الديناميكي والمعزول لموديولات الموردين
        # الاستقلالية: كل موديول يحمل مساحته الخاصة ولا يتأثر بالآخرين
        apps_dir = app.root_path
        for folder in os.listdir(apps_dir):
            if folder.startswith('suppliers_'):
                registry_path = os.path.join(apps_dir, folder, 'registry.py')
                if os.path.exists(registry_path):
                    try:
                        # استيراد ديناميكي معزول
                        module = importlib.import_module(f"apps.{folder}.registry")
                        if hasattr(module, 'register_module'):
                            # تمرير التطبيق للموديول ليقوم بتسجيل نفسه بشكل مستقل
                            module.register_module(app)
                    except Exception as e:
                        # الاستقلالية: إذا فشل موديول، يستمر التطبيق في العمل للموديولات الأخرى
                        print(f"⚠️ [Registry] تعذر تسجيل الموديول {folder}: {e}")

        # 6. فرض تهيئة جميع العلاقات المكتشفة
        db.configure_mappers()

    @app.route('/')
    def index():
        return redirect(url_for('auth_portal.login'))

    # 7. تهيئة البيانات الأولية (Seed)
    with app.app_context():
        try:
            from apps.models import AdminUser, Supplier
            
            # زرع المسؤول
            if not AdminUser.query.filter_by(username='علي محجوب').first():
                admin = AdminUser(username='علي محجوب', role='Owner', phone_number='779077746')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
            
            # زرع المورد
            if not Supplier.query.filter_by(username='وائل محجوب').first():
                new_supplier = Supplier(
                    username='وائل محجوب',
                    trade_name='متجر وائل محجوب',
                    phone='779077746',
                    search_phone='779077746'
                )
                new_supplier.set_password('123')
                db.session.add(new_supplier)
                db.session.commit()
                
        except Exception as e:
            print(f"⚠️ [Database Setup] خطأ: {e}")

    return app
