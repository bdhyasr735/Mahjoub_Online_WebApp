# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, redirect, session, url_for, request
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS 
from werkzeug.routing import BuildError
import config
from apps.extensions import db, login_manager, migrate

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

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )

    CORS(app, resources={r"/admin/*": {"origins": ["https://studio.apollographql.com", "http://localhost:5000"]}}, supports_credentials=True)

    db.init_app(app)
    
    # ============================================================
    # ✅ إعادة بناء الجداول (Drop & Create) مع CASCADE
    # ============================================================
    with app.app_context():
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        from apps.models.product_db import Product
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.financials_db import OrderFinancial
        from apps.models.orders_db import Order
        from apps.models.order_items_db import OrderItem
        from apps.models.supplier_profile_db import SupplierProfile
        from apps.models.product_supplier_map import ProductSupplierMapping
        from apps.models.sync_log import SyncLog
        from apps.models.marketer_db import Marketer
        from apps.models.admin_staff_db import AdminStaff
        
        # ✅ حذف جميع الجداول مع CASCADE (لتجاوز مشكلة التبعيات)
        print("🔄 [DB]: جاري حذف جميع الجداول مع CASCADE...")
        try:
            # استخدام SQL خام لحذف جميع الجداول مع CASCADE
            from sqlalchemy import text
            db.session.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
            db.session.commit()
            print("✅ [DB]: تم حذف وإعادة إنشاء الـ Schema بنجاح.")
        except Exception as e:
            print(f"⚠️ [DB]: فشل حذف الـ Schema: {e}")
            print("🔄 [DB]: محاولة الحذف باستخدام db.drop_all()...")
            db.drop_all()
            print("✅ [DB]: تم حذف جميع الجداول باستخدام db.drop_all().")
        
        print("🔄 [DB]: جاري إنشاء الجداول من جديد...")
        db.create_all()
        print("✅ [DB]: تم إنشاء جميع الجداول بنجاح.")

        # ✅ زراعة المالك "علي محجوب"
        if not AdminUser.query.filter_by(username='ali_mahjoub').first():
            new_admin = AdminUser(username='ali_mahjoub', role='Owner')
            new_admin.set_password('123')
            db.session.add(new_admin)
            db.session.commit()
            print("✅ [Seed]: تم زرع المالك علي محجوب بنجاح.")
        
        # ✅ زراعة مورد تجريبي (اختياري)
        if not Supplier.query.filter_by(username='test_supplier').first():
            test_supplier = Supplier(
                username='test_supplier',
                trade_name='متجر تجريبي',
                owner_name='محمد التجريبي',
                phone='0500000000',
                status='active'
            )
            test_supplier.set_password('123')
            db.session.add(test_supplier)
            db.session.flush()
            
            # ✅ إنشاء محفظة للمورد التجريبي
            wallet = SupplierWallet(
                supplier_id=test_supplier.id,
                wallet_code=f"MAH-WEL963{test_supplier.id}",
                balance_sar=1000.00
            )
            db.session.add(wallet)
            db.session.commit()
            print("✅ [Seed]: تم زرع مورد تجريبي test_supplier / 123")

    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # ✅ استثناء CSRF لبوابة الموردين
    from apps.suppliers_auth_portal.routes import suppliers_bp
    csrf.exempt(suppliers_bp)
    
    limiter.init_app(app)

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

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin'):
            return redirect(os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x'))
        return redirect(url_for('suppliers_auth.login'))

    # إعداد السياسة الأمنية (CSP)
    talisman.init_app(app, 
        content_security_policy={
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com"],
            'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com"],
            'img-src': ["'self'", "data:", "https://*"],
            'connect-src': ["'self'", "https://ckeditor.com", "https://*.ckeditor.com"]
        },
        force_https=(os.environ.get('FLASK_ENV') == 'production')
    )

    try:
        from apps.admin.graphql_routes import graphql_bp 
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp) 
    except ImportError:
        pass

    # تسجيل الموديولات ديناميكياً
    apps_dir = app.root_path
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'admin']
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

    # ✅ إضافة فلتر Jinja لتوليد CSRF token داخل القوالب
    @app.context_processor
    def inject_vars():
        def safe_url_for(endpoint, **values):
            try: return url_for(endpoint, **values)
            except BuildError:
                alt_endpoint = f"{endpoint}_bp" if not endpoint.endswith('_bp') else endpoint.replace('_bp', '')
                try: return url_for(alt_endpoint, **values)
                except BuildError: return '#'
        return dict(
            csrf_token=generate_csrf,
            registered_modules=ADMIN_MODULES,
            supplier_modules=SUPPLIER_MODULES,
            safe_url_for=safe_url_for
        )

    return app
