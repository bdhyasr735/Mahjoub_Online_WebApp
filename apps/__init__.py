# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask
from flask_wtf.csrf import CSRFProtect, generate_csrf
from apps.extensions import db, login_manager, migrate
from apps.utils.time_utils import format_full_timestamp

csrf = CSRFProtect()

# قاموس لتخزين بيانات الموديولات المكتشفة تلقائياً
REGISTERED_MODULES = {}

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # تسجيل الـ Blueprints الأساسية للإدارة فقط
    from apps.auth_portal.routes import auth_portal
    app.register_blueprint(auth_portal, url_prefix='/auth')
    
    # إضافة الفلاتر المخصصة
    app.jinja_env.filters['full_time'] = format_full_timestamp

    # إعداد الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # الحقن المباشر للمتغيرات لضمان وصول الموديولات للشريط الجانبي
    @app.context_processor
    def inject_vars():
        return dict(
            csrf_token=generate_csrf,
            registered_modules=REGISTERED_MODULES
        )

    with app.app_context():
        db.create_all()

        # زرع المستخدم الافتراضي (المدير)
        try:
            from apps.models.admin_db import AdminUser
            admin = AdminUser.query.filter_by(username='علي محجوب').first()
            if not admin:
                admin = AdminUser(username='علي محجوب')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ أثناء إنشاء المستخدم الافتراضي: {e}")

        # [نظام التسجيل التلقائي للموديولات]
        apps_dir = app.root_path
        # استبعاد المجلدات التي لا تحتاج تسجيل تلقائي أو التي تسبب مشاكل
        ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'suppliers_auth', 'auth_portal', 'admin_dashboard']
        
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if os.path.isdir(item_path) and item not in ignored_dirs:
                registry_file = os.path.join(item_path, 'registry.py')
                if os.path.exists(registry_file):
                    try:
                        # استيراد الموديول ديناميكياً
                        module = importlib.import_module(f"apps.{item}.registry")
                        if hasattr(module, 'register_module'):
                            module.register_module(app)
                            
                            # تخزين البيانات ليقرأها نظام القوالب تلقائياً
                            REGISTERED_MODULES[item] = {
                                "display_name": getattr(module, 'MODULE_NAME', item.capitalize()),
                                "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                                "links": getattr(module, 'LINKS', {}),
                                "active": True
                            }
                            print(f"✅ [Auto-Discovery] تم تسجيل موديول: {item}")
                    except Exception as e:
                        print(f"⚠️ [Auto-Discovery] خطأ في الموديول {item}: {e}")
                        REGISTERED_MODULES[item] = {"active": False}

    # تحديث الـ Config بـ خريطة المسارات لتفادي BuildError في القوالب
    app.config['ENDPOINT_MAP'] = {rule.endpoint for rule in app.url_map.iter_rules()}

    return app
