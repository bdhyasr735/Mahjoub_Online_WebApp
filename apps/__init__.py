import os
import importlib
import logging
from flask import Flask, redirect, session
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
limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "100 per hour"], storage_uri="memory://")

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    config.Config.validate_config()

    # إعدادات أمان الكوكيز
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )

    CORS(app, resources={r"/admin/*": {"origins": ["https://studio.apollographql.com", "http://localhost:5000"]}}, supports_credentials=True)

    # 1. تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # 2. تحميل المستخدم
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        user_type = session.get('user_type')
        if user_type == 'admin': return db.session.get(AdminUser, int(user_id))
        elif user_type == 'supplier': return db.session.get(Supplier, int(user_id))
        elif user_type == 'staff': return db.session.get(SupplierStaff, int(user_id))
        return db.session.get(AdminUser, int(user_id)) or db.session.get(Supplier, int(user_id)) or db.session.get(SupplierStaff, int(user_id))

    # 3. الأمان و الـ Talisman
    talisman.init_app(app, 
        content_security_policy={
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'img-src': ["'self'", "data:", "https://*"]
        },
        force_https=(os.environ.get('FLASK_ENV') == 'production')
    )

    login_manager.login_view = 'suppliers_auth.login'

    # 4. تسجيل الـ Blueprints
    app.register_blueprint(qomrah_bp)
    csrf.exempt(qomrah_bp)
    
    try:
        from apps.admin.graphql_routes import graphql_bp 
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp) 
    except ImportError:
        pass

    # 5. تسجيل الموديولات الديناميكي
    apps_dir = app.root_path
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'admin', 'auth']
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
                            # تسجيل البيانات في القواميس للعرض في الواجهة
                            module_links = getattr(module, 'LINKS', {})
                            if module_links:
                                mod_data = {
                                    "display_name": getattr(module, 'MODULE_NAME', item.replace('_', ' ').capitalize()),
                                    "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                                    "links": module_links,
                                }
                                if getattr(module, 'SHOW_IN_SUPPLIER', False):
                                    SUPPLIER_MODULES[item] = mod_data
                                else:
                                    ADMIN_MODULES[item] = mod_data
                    except Exception as e:
                        print(f"❌ [Registry]: خطأ في تسجيل موديول {item}: {e}")

    # 6. المسارات الأساسية و الـ Context Processor
    @app.route('/')
    def index():
        return redirect('/supplier/login')

    @app.context_processor
    def inject_vars():
        return dict(
            csrf_token=generate_csrf,
            registered_modules=ADMIN_MODULES,
            supplier_modules=SUPPLIER_MODULES,
            url_map=app.url_map
        )

    return app
