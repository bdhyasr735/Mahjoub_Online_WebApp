# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
import secrets
import string
import click
from datetime import datetime
from flask import Flask, redirect, session, url_for, request, jsonify, render_template, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_cors import CORS
from werkzeug.routing import BuildError
from sqlalchemy import text, select
import config
from apps.extensions import db, login_manager, migrate, limiter
from apps.services.graphql_client import GraphQLClient

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}


def import_all_models():
    """استيراد جميع ملفات النماذج تلقائياً من مجلد apps/models لضمان التعرف على جميع الجداول"""
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                try:
                    importlib.import_module(f"apps.models.{module_name}")
                except Exception as e:
                    print(f"⚠️ [Model Import Error] فشل استيراد {module_name}: {e}")


def seed_database():
    """زراعة البيانات المبدئية وتسجيل حركة الرصيد الافتتاحي بشكل ديناميكي وآمن"""
    try:
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
        from apps.models.treasury_db import TreasuryEntry
    except ImportError as ie:
        print(f"⚠️ [Seed Import Warning]: تعذر استيراد بعض النماذج أثناء الزراعة: {ie}")
        return

    # 1. زراعة المالك
    try:
        if not AdminUser.query.filter_by(username='ali_mahjoub').first():
            admin = AdminUser(username='ali_mahjoub', role='Owner')
            admin.set_password('123')
            db.session.add(admin)
            db.session.commit()
            print("✅ [Seed]: تم زرع المالك (ali_mahjoub) بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Seed Error - Admin]: {e}")

    # 2. زراعة موظف إدارة
    try:
        existing_staff = AdminStaff.query.filter_by(username='admin_staff_test').first()
        if not existing_staff:
            staff = AdminStaff(
                username='admin_staff_test',
                name='موظف الإدارة التجريبي',
                email='admin_staff@mahjoub.online',
                role_title='مشرف عام الإدارة',
                is_active=True,
                permissions={'manage_staff': True, 'manage_suppliers': True, 'manage_products': True}
            )
            staff.set_password('123')
            db.session.add(staff)
            db.session.commit()
            print("✅ [Seed]: تم زرع موظف الإدارة التجريبي بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Seed Error - Staff]: {e}")

    # 3. زراعة مورد ومحفظته وقيد الخزينة العامة
    try:
        if not Supplier.query.filter_by(username='test_supplier').first():
            supplier = Supplier(
                username='test_supplier',
                trade_name='متجر تجريبي',
                owner_name='المورد التجريبي',
                phone='779077746',
                status='active',
                supplier_code='SUP9631'
            )
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()

            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL963{supplier.id}",
                balance_sar=1000000.00
            )
            db.session.add(wallet)
            db.session.flush()

            now = datetime.utcnow()
            date_str = now.strftime('%Y%m%d')
            time_stamp = now.strftime('%H%M%S%f')[:9]
            characters = string.ascii_uppercase + string.digits
            
            while True:
                random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
                candidate_ref = f"TRX-{supplier.supplier_code}-{date_str}-{time_stamp}-{random_6_code}"
                
                exists_ref = db.session.scalar(
                    select(WalletTransaction.id).where(WalletTransaction.reference_number == candidate_ref)
                )
                if not exists_ref:
                    seed_ref_number = candidate_ref
                    break

            seed_voucher_number = generate_unique_voucher_number(db.session.connection(), length=6, prefix="VCH-")

            initial_transaction = WalletTransaction(
                wallet_id=wallet.id,
                trans_type='deposit',
                status='completed',
                amount=1000000.00,
                currency='SAR',
                reference_number=seed_ref_number,
                voucher_number=seed_voucher_number,
                description="رصيد افتتاحي للمورد التجريبي عند إعداد المحفظة"
            )
            db.session.add(initial_transaction)

            treasury_entry = TreasuryEntry(
                reference_number=seed_ref_number,
                voucher_number=seed_voucher_number,
                entry_type='deposit',
                amount=1000000.00,
                currency='SAR',
                owner_type='supplier',
                owner_id=supplier.id,
                description="سند إيداع رصيد افتتاحي للمورد التجريبي (الخزينة العامة)"
            )
            db.session.add(treasury_entry)

            db.session.commit()
            print(f"✅ [Seed]: تم زرع المورد والمحفظة وخزينة الرصيد الافتتاحي (1,000,000 SAR) بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Seed Error - Supplier]: {e}")


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
    # ⚙️ إعادة بناء الجداول تلقائياً عند التشغيل بناءً على متغير البيئة
    # ============================================================
    with app.app_context():
        import_all_models()
        
        if os.environ.get('RESET_DB_ON_START') == 'true':
            try:
                db.session.execute(text("DROP SCHEMA public CASCADE;"))
                db.session.execute(text("CREATE SCHEMA public;"))
                db.session.commit()
                db.create_all()
                seed_database()
                print("✅ [Schema Reset]: تم مسح وإعادة بناء القاعدة وزراعة البيانات بنجاح.")
            except Exception as e:
                db.session.rollback()
                print(f"⚠️ [Schema Reset Error]: {e}")
        else:
            try:
                db.create_all()
            except Exception as e:
                print(f"❌ [Schema Create Error]: {e}")

    # ============================================================
    # ⚙️ أمر CLI لإعادة بناء القاعدة يدوياً
    # ============================================================
    @app.cli.command("rebuild-db")
    def rebuild_db_command():
        """حذف جميع الجداول وإعادة إنشائها وزراعة البيانات المبدئية عبر السطر البرمجي."""
        click.echo("🔄 [DB Rebuild]: جاري حذف جميع الجداول...")
        import_all_models()
        try:
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()
            click.echo("✅ [Schema Reset]: تم مسح وإعادة إنشاء الـ Schema بنجاح (CASCADE).")
        except Exception as e:
            db.session.rollback()
            click.echo(f"⚠️ [Schema Reset Error]: {e}")

        click.echo("⚙️ [DB Rebuild]: جاري إنشاء الجداول بالهيكل الجديد...")
        db.create_all()
        click.echo("✅ [Schema Create]: تم إنشاء جميع الجداول بنجاح.")

        click.echo("🌱 [DB Rebuild]: جاري زراعة البيانات المبدئية وتوثيق السندات...")
        seed_database()
        click.echo("🎉 [DB Rebuild]: اكتملت عملية إعادة البناء والتسجيل بنجاح!")

    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return None
            
        user_type = session.get('user_type')
        
        if user_type == 'admin': 
            return db.session.get(AdminUser, user_id_int)
        elif user_type == 'admin_staff':
            return db.session.get(AdminStaff, user_id_int)
        elif user_type == 'supplier_staff':
            return db.session.get(SupplierStaff, user_id_int)
        elif user_type == 'supplier': 
            return db.session.get(Supplier, user_id_int)
        elif user_type == 'staff': 
            staff_admin = db.session.get(AdminStaff, user_id_int)
            if staff_admin:
                return staff_admin
            return db.session.get(SupplierStaff, user_id_int)

        return (
            db.session.get(AdminUser, user_id_int) or 
            db.session.get(AdminStaff, user_id_int) or
            db.session.get(Supplier, user_id_int) or
            db.session.get(SupplierStaff, user_id_int)
        )

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/supplier'):
            return redirect(url_for('suppliers_auth.login'))
        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
        return redirect(admin_login_path)

    @app.before_request
    def protect_routes():
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff

        path = request.path
        
        if '/static/' in path or path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.woff2')):
            return

        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')

        exempt_prefixes = [
            '/static', 
            '/graphql', 
            '/admin/graphql', 
            '/favicon.ico', 
            '/m7jb_test_connection', 
            '/supplier/login', 
            '/supplier/register',
            '/supplier/forgot-password',
            admin_login_path, 
            '/auth',
            '/api/whatsapp'
        ]

        if path == '/' or any(path.startswith(p) for p in exempt_prefixes):
            return

        if current_user.is_authenticated:
            is_admin_side = isinstance(current_user, (AdminUser, AdminStaff))
            is_supplier_side = isinstance(current_user, (Supplier, SupplierStaff))

            if path.startswith('/admin') or path.startswith('/dashboard'):
                if is_admin_side:
                    return
                return redirect(url_for('suppliers_auth.login'))

            if path.startswith('/supplier'):
                if is_supplier_side:
                    return
                return redirect(admin_login_path)

            return

        if path.startswith('/supplier'):
            return redirect(url_for('suppliers_auth.login'))

        return redirect(admin_login_path)

    talisman = Talisman()
    talisman.init_app(app, 
        content_security_policy={
            'default-src': ["'self'"],
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com", "https://cdn.tailwindcss.com"],
            'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://ckeditor.com", "https://cdn.tailwindcss.com"],
            'img-src': ["'self'", "data:", "https://*"],
            'connect-src': ["'self'", "https://ckeditor.com", "https://*.ckeditor.com", "https://mahjoub.online", "https://studio.apollographql.com", "https://embed.apollographql.com", "https://sandbox.embed.apollographql.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
            'frame-ancestors': ["'self'", "https://studio.apollographql.com", "https://embed.apollographql.com", "https://sandbox.embed.apollographql.com"]
        },
        force_https=(os.environ.get('FLASK_ENV') == 'production')
    )

    @app.route('/admin/graphql', methods=['GET', 'POST', 'OPTIONS'])
    @csrf.exempt
    def graphql_proxy():
        origin = request.headers.get('Origin', 'https://studio.apollographql.com')
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Apollo-Require-Preflight, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            return response
        try:
            if request.method == 'GET':
                query = request.args.get('query')
                variables = request.args.get('variables')
                operation_name = request.args.get('operationName')
            else:
                data = request.get_json(silent=True) or {}
                query = data.get('query')
                variables = data.get('variables')
                operation_name = data.get('operationName')
            client = GraphQLClient()
            result = client.execute(query, variables, operation_name)
            response = jsonify(result)
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        except Exception as e:
            response = jsonify({"error": str(e), "message": "فشل تمرير طلب GraphQL إلى الخادم"})
            response.status_code = 500
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response

    @app.route('/m7jb_test_connection')
    def test_graphql_connection():
        try:
            client = GraphQLClient()
            success = client.test_connection()
            return jsonify({"connection_status": success, "endpoint": client.endpoint, "message": "✅ الاتصال ناجح" if success else "❌ فشل الاتصال"})
        except Exception as e:
            return jsonify({"connection_status": False, "error": str(e), "message": f"❌ خطأ: {str(e)}"}), 500

    @app.route('/')
    def index():
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        
        if current_user.is_authenticated:
            if isinstance(current_user, (Supplier, SupplierStaff)):
                return redirect('/supplier/dashboard')
            return redirect('/dashboard')
            
        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
        return redirect(admin_login_path)

    try:
        from apps.auth_portal.routes import auth_portal
        app.register_blueprint(auth_portal)
    except Exception as e:
        print(f"❌ [Portal]: خطأ في تسجيل بوابة المصادقة الإدارية: {e}")

    try:
        from apps.suppliers_auth_portal.routes import suppliers_bp
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        csrf.exempt(suppliers_bp)
    except Exception as e:
        print(f"❌ [Portal]: خطأ في تسجيل بوابة الموردين: {e}")

    try:
        from apps.admin.graphql_routes import graphql_bp 
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp)
    except ImportError:
        pass

    # ============================================================
    # 🔄 التسجيل الديناميكي التلقائي للموديولات عبر ملف الـ registry.py
    # ============================================================
    apps_dir = app.root_path
    ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'api', 'data', 'auth_portal', 'suppliers_auth_portal', 'admin', 'zsa_engine']
    
    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if not os.path.isdir(item_path) or item in ignored_dirs:
                continue
            registry_file = os.path.join(item_path, 'registry.py')
            if os.path.exists(registry_file):
                try:
                    module = importlib.import_module(f"apps.{item}.registry")
                    if hasattr(module, 'register_module'):
                        module.register_module(app)
                    links_data = {}
                    if hasattr(module, 'NAV_ITEMS') and isinstance(module.NAV_ITEMS, list):
                        for nav in module.NAV_ITEMS:
                            ep = nav.get('endpoint')
                            title = nav.get('title')
                            if ep and title:
                                links_data[ep] = title
                    if not links_data and hasattr(module, 'LINKS'):
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
                            "display_name": getattr(module, 'MODULE_NAME', getattr(module, 'DISPLAY_NAME', item.replace('_', ' ').capitalize())),
                            "icon": getattr(module, 'MODULE_ICON', getattr(module, 'ICON', 'fa-folder')),
                            "links": links_data,
                        }
                        if getattr(module, 'SHOW_IN_SUPPLIER', False): 
                            SUPPLIER_MODULES[item] = mod_data
                        else: 
                            ADMIN_MODULES[item] = mod_data
                except Exception as e:
                    print(f"❌ [Registry]: خطأ في تسجيل موديول '{item}': {e}")

    @app.context_processor
    def inject_vars():
        def safe_url_for(endpoint, **values):
            try: return url_for(endpoint, **values)
            except Exception: return '#'
            
        supplier_context = {
            'current_supplier': None, 'owner_full_name': '', 'supplier_bank_name': '',
            'supplier_bank_account': '', 'supplier_wallet': None,
            'pending_financials_count': 0, 'total_pending_payouts': 0.00
        }
        if current_user.is_authenticated:
            try:
                user_type = session.get('user_type')
                if user_type in ['supplier', 'supplier_staff', 'staff']:
                    supplier_id = getattr(current_user, 'supplier_id', None) if user_type != 'supplier' else getattr(current_user, 'id', None)
                    if supplier_id:
                        from apps.models.supplier_db import Supplier
                        from apps.models.wallet_db import SupplierWallet
                        supplier_obj = db.session.get(Supplier, supplier_id)
                        if supplier_obj:
                            wallet_obj = SupplierWallet.query.filter_by(supplier_id=supplier_obj.id).first()
                            supplier_context.update({
                                'current_supplier': supplier_obj,
                                'owner_full_name': getattr(supplier_obj, 'owner_name', ''),
                                'supplier_bank_name': getattr(supplier_obj, 'bank_name', ''),
                                'supplier_bank_account': getattr(supplier_obj, 'bank_account_number', ''),
                                'supplier_wallet': wallet_obj
                            })
            except Exception as e:
                print(f"⚠️ [Context Processor Error]: {e}")

        return {
            'registered_modules': ADMIN_MODULES,
            'admin_modules': ADMIN_MODULES,
            'supplier_modules': SUPPLIER_MODULES,
            'safe_url_for': safe_url_for,
            **supplier_context
        }

    @app.after_request
    def set_csrf_header(response):
        if not response.headers.get('X-CSRF-Token'):
            response.headers['X-CSRF-Token'] = generate_csrf()
        return response

    return app
