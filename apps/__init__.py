# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, redirect, session, url_for, request, jsonify, render_template, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS 
from werkzeug.routing import BuildError
import config
from apps.extensions import db, login_manager, migrate
from apps.services.graphql_client import GraphQLClient

# تهيئة الأدوات
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "100 per hour"], storage_uri="memory://")

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}

def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config.from_object('config.Config')
    config.Config.validate_config()

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )

    app.jinja_env.globals.update(getattr=getattr)

    # ✅ حل جذري وشامل لـ CORS للسماح لـ Apollo Sandbox والأدوات الخارجية بالاتصال وتمرير الجلسات
    CORS(app, resources={
        r"/admin/graphql*": {
            "origins": [
                "https://studio.apollographql.com", 
                "https://embed.apollographql.com", 
                "https://sandbox.embed.apollographql.com",
                "http://localhost:5000", 
                "https://mahjoub.online"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "X-Requested-With", 
                "Apollo-Require-Preflight",
                "Accept"
            ],
            "supports_credentials": True
        }
    })

    db.init_app(app)
    
    # ============================================================
    # ✅ إعادة بناء الجداول تلقائياً وتحديث الأعمدة والزراعة
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
        
        print("🔄 [DB]: جاري إعادة ضبط وبناء الجداول بالهيكلة الكاملة...")
        
        db.session.execute(db.text('DROP SCHEMA public CASCADE; CREATE SCHEMA public;'))
        db.session.commit()
        db.create_all()
        print("✅ [DB]: تم إعادة إنشاء جميع الجداول بنجاح.")

        # ✅ 1. زراعة المالك
        try:
            admin = AdminUser(username='ali_mahjoub', role='Owner')
            admin.set_password('123')
            db.session.merge(admin)
            db.session.commit()
            print("✅ [Seed]: تم زرع المالك علي محجوب بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ في زراعة المالك: {e}")

        # ✅ 2. زراعة موظف إدارة
        try:
            staff = AdminStaff(
                username='admin_staff_test',
                name='موظف الإدارة التجريبي',
                email='admin_staff@mahjoub.online',
                role_title='مشرف عام الإدارة',
                is_active=True,
                permissions={'manage_staff': True, 'manage_suppliers': True, 'manage_products': True}
            )
            staff.set_password('123')
            db.session.merge(staff)
            db.session.commit()
            print("✅ [Seed]: تم زرع موظف الإدارة افتراضياً.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ في زراعة موظف الإدارة: {e}")
        
        # ✅ 3. زراعة مورد
        try:
            supplier = Supplier(
                username='test_supplier',
                trade_name='متجر تجريبي',
                owner_name='المورد التجريبي',
                phone='0500000000',
                status='active'
            )
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()
                
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL963{supplier.id}",
                balance_sar=1000.00
            )
            db.session.add(wallet)
            db.session.commit()
            print("✅ [Seed]: تم زرع مورد تجريبي مع محفظة.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ في زراعة المورد التجريبي: {e}")

        # ✅ 4. زراعة موظف مورد
        try:
            sup = Supplier.query.filter_by(username='test_supplier').first()
            if sup:
                s_staff = SupplierStaff(
                    supplier_id=sup.id,
                    username='supplier_staff_test',
                    name='موظف المورد التجريبي',
                    email='supplier_staff@mahjoub.online',
                    role_title='مسؤول مبيعات المورد',
                    is_active=True,
                    permissions={'manage_catalog': True, 'process_orders': True}
                )
                s_staff.set_password('123')
                db.session.merge(s_staff)
                db.session.commit()
                print("✅ [Seed]: تم زرع موظف المورد افتراضياً.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ في زراعة موظف المورد: {e}")

        # ✅ 5. زراعة منتج تجريبي
        try:
            sup = Supplier.query.filter_by(username='test_supplier').first()
            if sup:
                mapping = ProductSupplierMapping(
                    product_qid='TEST_PROD_001',
                    supplier_id=sup.id,
                    price=100.00,
                    quantity=10,
                    status='active'
                )
                db.session.merge(mapping)
                db.session.commit()
                print(f"✅ [Seed]: تم ربط منتج تجريبي بالمورد.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ في زراعة المنتج التجريبي: {e}")

    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        
        user_id_int = int(user_id)
        user_type = session.get('user_type')
        
        if user_type == 'admin': 
            return db.session.get(AdminUser, user_id_int)
        elif user_type == 'staff': 
            staff_admin = db.session.get(AdminStaff, user_id_int)
            if staff_admin:
                return staff_admin
            return db.session.get(SupplierStaff, user_id_int)
        elif user_type == 'supplier': 
            return db.session.get(Supplier, user_id_int)
        return (
            db.session.get(Supplier, user_id_int) or
            db.session.get(SupplierStaff, user_id_int) or
            db.session.get(AdminUser, user_id_int) or 
            db.session.get(AdminStaff, user_id_int)
        )

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/supplier'):
            return redirect(url_for('suppliers_auth.login'))
        return redirect(os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x'))

    @app.before_request
    def protect_routes():
        path = request.path
        exempt_prefixes = ['/static', '/auth', '/supplier/login', '/supplier/register', '/graphql', '/favicon.ico', '/m7jb_test_connection', '/admin/graphql']
        if path == '/' or any(path.startswith(p) for p in exempt_prefixes):
            return

        if current_user.is_authenticated:
            user_type = session.get('user_type')
            if path.startswith('/admin') or path.startswith('/dashboard'):
                if user_type in ['admin', 'staff']:
                    return  
                else:
                    return redirect(os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x'))
            if path.startswith('/supplier'):
                if user_type in ['supplier', 'staff']:
                    return  
                else:
                    return redirect(url_for('suppliers_auth.login'))
            return  

        if path.startswith('/supplier'):
            return redirect(url_for('suppliers_auth.login'))
        if path.startswith('/admin') or path.startswith('/dashboard'):
            admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
            return redirect(admin_login_path)
        
        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
        if not path.startswith(admin_login_path):
            return redirect(admin_login_path)

    talisman.init_app(app, 
        content_security_policy={
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com"],
            'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com"],
            'img-src': ["'self'", "data:", "https://*"],
            'connect-src': [
                "'self'", 
                "https://ckeditor.com", 
                "https://*.ckeditor.com", 
                "https://mahjoub.online",
                "https://studio.apollographql.com",
                "https://embed.apollographql.com",
                "https://sandbox.embed.apollographql.com",
                "https://cdn.jsdelivr.net", 
                "https://cdnjs.cloudflare.com"
            ],
            'frame-ancestors': [
                "'self'",
                "https://studio.apollographql.com",
                "https://embed.apollographql.com",
                "https://sandbox.embed.apollographql.com"
            ]
        },
        force_https=(os.environ.get('FLASK_ENV') == 'production')
    )

    # ============================================================
    # ✅ المسار الجديد: محطة عبور GraphQL لـ Apollo Sandbox (مضبوط بالكامل)
    # ============================================================
    @app.route('/admin/graphql', methods=['GET', 'POST', 'OPTIONS'])
    @csrf.exempt  # إعفاء تام من حماية CSRF لطلبات الساندبوكس الخارجية
    def graphql_proxy():
        origin = request.headers.get('Origin', 'https://studio.apollographql.com')

        # الاستجابة الصحيحة الكاملة لطلبات اختبار الاتصال المسبق Preflight
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Apollo-Require-Preflight, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            return response

        try:
            # معالجة استعلامات GET (غالباً ما يستخدمها Apollo Sandbox لجلب Schema Introspection)
            if request.method == 'GET':
                query = request.args.get('query')
                variables = request.args.get('variables')
                operation_name = request.args.get('operationName')
            else:
                data = request.get_json(silent=True) or {}
                query = data.get('query')
                variables = data.get('variables')
                operation_name = data.get('operationName')

            # استخدام عميل GraphQL لتمرير الطلب للخادم الفعلي
            client = GraphQLClient()
            result = client.execute(query, variables, operation_name)

            response = jsonify(result)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

        except Exception as e:
            print(f"❌ [GraphQL Proxy Error]: {str(e)}")
            response = jsonify({
                "error": str(e),
                "message": "فشل تمرير طلب GraphQL إلى الخادم"
            })
            response.status_code = 500
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

    # ============================================================
    # ✅ مسار اختبار الاتصال بـ GraphQL
    # ============================================================
    @app.route('/m7jb_test_connection')
    def test_graphql_connection():
        try:
            client = GraphQLClient()
            success = client.test_connection()
            return jsonify({
                "connection_status": success,
                "endpoint": client.endpoint,
                "message": "✅ الاتصال ناجح" if success else "❌ فشل الاتصال"
            })
        except Exception as e:
            return jsonify({
                "connection_status": False,
                "error": str(e),
                "message": f"❌ خطأ: {str(e)}"
            }), 500

    @app.route('/')
    def index():
        return redirect(os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x'))

    try:
        from apps.auth_portal.routes import auth_portal
        app.register_blueprint(auth_portal)
        print("✅ [Portal]: تم تسجيل بوابة المصادقة الإدارية بنجاح.")
    except Exception as e:
        print(f"❌ [Portal]: خطأ في تسجيل بوابة المصادقة الإدارية: {e}")

    try:
        from apps.suppliers_auth_portal.routes import suppliers_bp
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        csrf.exempt(suppliers_bp)
        print("✅ [Portal]: تم تسجيل بوابة الموردين بنجاح تحت المسار /supplier.")
    except Exception as e:
        print(f"❌ [Portal]: خطأ في تسجيل بوابة الموردين: {e}")

    try:
        from apps.admin.graphql_routes import graphql_bp 
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp)
        print("✅ [Portal]: تم تسجيل GraphQL بنجاح.")
    except ImportError:
        pass

    # ============================================================
    # ✅ البحث عن الموديولات الديناميكية وتسجيلها تلقائياً
    # ============================================================
    apps_dir = app.root_path
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'data', 'auth_portal', 'suppliers_auth_portal', 'admin']
    
    print("🔄 [Registry]: جارٍ البحث عن الموديولات الإضافية...")
    
    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            if not os.path.isdir(item_path) or item in ignored_dirs:
                continue
                
            registry_file = os.path.join(item_path, 'registry.py')
            if os.path.exists(registry_file):
                try:
                    print(f"🔍 [Registry]: جارٍ تحميل موديول '{item}'...")
                    module = importlib.import_module(f"apps.{item}.registry")
                    
                    if hasattr(module, 'register_module'):
                        module.register_module(app)
                        print(f"✅ [Registry]: تم تسجيل موديول '{item}' بنجاح.")
                    else:
                        print(f"⚠️ [Registry]: الموديول '{item}' لا يحتوي على register_module")
                    
                    links_data = None
                    if hasattr(module, 'LINKS'):
                        raw_links = getattr(module, 'LINKS')
                        if isinstance(raw_links, dict):
                            links_data = {ep: lbl for ep, lbl in raw_links.items()}
                        elif isinstance(raw_links, list):
                            links_data = {ep: lbl for ep, lbl in raw_links}

                    menu_items_func = getattr(module, 'get_menu_items', None)
                    if not links_data and menu_items_func:
                        res = menu_items_func()
                        if isinstance(res, dict):
                            links_data = res
                        elif isinstance(res, list):
                            links_data = {ep: lbl for ep, lbl in res}

                    if links_data:
                        mod_data = {
                            "display_name": getattr(module, 'MODULE_NAME', item.replace('_', ' ').capitalize()),
                            "icon": getattr(module, 'MODULE_ICON', 'fa-folder'),
                            "links": links_data,
                        }
                        if getattr(module, 'SHOW_IN_SUPPLIER', False):
                            SUPPLIER_MODULES[item] = mod_data
                            print(f"    📌 [Supplier]: تمت إضافة '{mod_data['display_name']}' إلى قائمة الموردين")
                        else:
                            ADMIN_MODULES[item] = mod_data
                            print(f"    📌 [Admin]: تمت إضافة '{mod_data['display_name']}' إلى قائمة الإدارة")
                            
                except ImportError as e:
                    print(f"❌ [Registry]: خطأ في استيراد موديول '{item}': {e}")
                except Exception as e:
                    print(f"❌ [Registry]: خطأ في تسجيل موديول '{item}': {e}")

    print(f"✅ [Registry]: تم تسجيل {len(ADMIN_MODULES)} موديول للإدارة و {len(SUPPLIER_MODULES)} موديول للموردين.")
    
    print("\n📋 [Blueprints] المسجلة:")
    for bp_name in app.blueprints:
        print(f"  - {bp_name}")

    @app.context_processor
    def inject_vars():
        def safe_url_for(endpoint, **values):
            try:
                return url_for(endpoint, **values)
            except Exception:
                return '#'
        
        return dict(
            csrf_token=generate_csrf,
            registered_modules=ADMIN_MODULES,
            supplier_modules=SUPPLIER_MODULES,
            safe_url_for=safe_url_for
        )

    @app.errorhandler(500)
    def handle_500_error(e):
        if request.path.startswith('/admin/orders') and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'حدث خطأ داخلي في الخادم أثناء معالجة الطلب.'}), 500
        return render_template('errors/500.html'), 500

    return app
