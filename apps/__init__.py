# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, redirect
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS 
import config

from apps.extensions import db, login_manager, migrate
from apps.api.qomrah_webhook import qomrah_bp 

# تهيئة الأدوات
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # التحقق من الإعدادات الحساسة
    config.Config.validate_config()

    # تفعيل CORS
    CORS(app, resources={r"/admin/*": {"origins": ["https://studio.apollographql.com", "http://localhost:5000"]}}, supports_credentials=True)

    # 1. تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # 2. إعدادات الأمان
    talisman.init_app(app, 
        content_security_policy={
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "https://cdn.datatables.net"],
            'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdn.datatables.net"],
            'img-src': ["'self'", "data:", "*"]
        },
        force_https=False
    )

    login_manager.login_view = 'suppliers_auth.login'

    # 3. تسجيل الـ Blueprints
    app.register_blueprint(qomrah_bp)
    csrf.exempt(qomrah_bp)
    
    try:
        from apps.admin.graphql_routes import graphql_bp 
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp) 
    except ImportError:
        pass

    # 4. تسجيل الموديولات الديناميكي
    apps_dir = app.root_path
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api']

    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if os.path.isdir(item_path) and item not in ignored_dirs:
                registry_file = os.path.join(item_path, 'registry.py')
                if os.path.exists(registry_file):
                    try:
                        module = importlib.import_module(f"apps.{item}.registry")
                        if hasattr(module, 'register_module'):
                            module.register_module(app)
                            mod_data = {
                                "display_name": getattr(module, 'MODULE_NAME', item.capitalize()),
                                "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                                "links": getattr(module, 'LINKS', {}),
                            }
                            if getattr(module, 'SHOW_IN_SUPPLIER', False):
                                SUPPLIER_MODULES[item] = mod_data
                            else:
                                ADMIN_MODULES[item] = mod_data
                    except Exception as e:
                        print(f"❌ [Registry]: خطأ في تسجيل موديول {item}: {e}")

    # 5. المسارات الأساسية
    @app.route('/')
    def index():
        return redirect('/supplier/login')

    @app.context_processor
    def inject_vars():
        return dict(
            csrf_token=generate_csrf,
            registered_modules=ADMIN_MODULES,
            supplier_modules=SUPPLIER_MODULES
        )

    # 6. إعداد البيئة الأولية وزرع المالك (علي محجوب)
    with app.app_context():
        # إنشاء الجداول أولاً
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️ [Setup]: تنبيه أثناء إنشاء الجداول: {e}")

        # زرع المالك في جدول الإدارة حصراً
        try:
            from apps.models.admin_db import AdminUser
            
            owner = AdminUser.query.filter_by(username='علي محجوب').first()
            if not owner:
                owner = AdminUser(username='علي محجوب', role='Owner')
                db.session.add(owner)
                db.session.flush() # لإعطاء ID قبل تعيين كلمة المرور إن لزم الأمر
                print("✅ [Setup]: تم إنشاء المستخدم المالك 'علي محجوب'.")
            
            # تحديث كلمة المرور لضمان القدرة على الدخول
            owner.set_password('123')
            db.session.commit()
            print("🔐 [Setup]: تم تأمين حساب المالك (علي محجوب) بكلمة المرور: 123.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ [Setup]: فشل زرع المستخدم المالك في جدول الإدارة: {e}")

    return app
