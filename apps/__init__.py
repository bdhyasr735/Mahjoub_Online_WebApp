# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from apps.extensions import db, login_manager, migrate
from apps.utils.time_utils import format_full_timestamp

# تهيئة الإضافات
csrf = CSRFProtect()
REGISTERED_MODULES = {}

@login_manager.user_loader
def load_user(user_id):
    try:
        from apps.models import AdminUser, Supplier, SupplierStaff
        user_type = session.get('user_type')
        uid = int(user_id)
        if user_type == 'admin': return AdminUser.query.get(uid)
        elif user_type == 'supplier': return Supplier.query.get(uid)
        elif user_type == 'staff': return SupplierStaff.query.get(uid)
        return AdminUser.query.get(uid) or Supplier.query.get(uid) or SupplierStaff.query.get(uid)
    except Exception as e:
        print(f"⚠️ خطأ في تحميل المستخدم: {e}")
        return None

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # 1. تهيئة الإضافات الأساسية
    app.jinja_env.filters['full_time'] = format_full_timestamp
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # --- تسجيل موديول الموردين (بوابة الدخول) ---
    from apps.suppliers_auth_portal.routes import suppliers_bp
    csrf.exempt(suppliers_bp) 
    app.register_blueprint(suppliers_bp, url_prefix='/supplier')

    login_manager.login_view = 'auth_portal.login'
    
    # 2. اكتشاف الموديولات وتسجيلها تلقائياً
    apps_dir = app.root_path 
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'suppliers_auth_portal']
    
    print(f"--- بدء اكتشاف الموديولات في: {apps_dir} ---")
    
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
                            REGISTERED_MODULES[item] = {
                                "display_name": getattr(module, 'MODULE_NAME', item.capitalize()),
                                "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                                "links": getattr(module, 'LINKS', {}),
                                "active": True
                            }
                            print(f"✅ [Auto-Discovery] تم تسجيل الموديول: {item}")
                    except Exception as e:
                        print(f"❌ [Auto-Discovery] فشل تسجيل الموديول {item}: {e}")

    # 3. حقن المتغيرات (Global Context)
    @app.context_processor
    def inject_vars():
        return dict(
            csrf_token=generate_csrf,
            registered_modules=REGISTERED_MODULES
        )

    # 4. تهيئة قاعدة البيانات والمسؤول
    with app.app_context():
        try:
            db.create_all()
            from apps.models import AdminUser
            admin = AdminUser.query.filter_by(username='علي محجوب').first()
            if not admin:
                admin = AdminUser(username='علي محجوب')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ تم إنشاء حساب المسؤول بنجاح.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء تهيئة قاعدة البيانات: {e}")
            db.session.rollback()

    return app
