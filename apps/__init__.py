# -*- coding: utf-8 -*-
# 📂 apps/__init__.py

import os
import importlib
import secrets
import string
import click
from datetime import datetime
from flask import Flask, redirect, session, url_for, request, jsonify, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_cors import CORS
from sqlalchemy import text, select
import config
from apps.extensions import db, login_manager, migrate, limiter
from apps.services.graphql_client import GraphQLClient

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}


def import_all_models():
    """استيراد جميع ملفات النماذج تلقائياً من مجلد apps/models لضمان التعرف على جميع الجداول والأنواع."""
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                try:
                    importlib.import_module(f"apps.models.{module_name}")
                except Exception as e:
                    print(f"⚠️ [خطأ في استيراد النموذج] فشل استيراد النموذج '{module_name}': {e}")


def seed_database():
    """
    زراعة البيانات المبدئية بشكل آمن وديناميكي مع التحقق الكامل من القيود والعلاقات.
    """
    try:
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
        from apps.models.treasury_db import TreasuryEntry
    except ImportError as ie:
        print(f"⚠️ [تحذير استيراد الزراعة]: تعذر استيراد بعض النماذج: {ie}")
        return

    # ============================================================
    # 1. زراعة حساب المالك (Owner)
    # ============================================================
    try:
        admin = AdminUser.query.filter_by(username='ali_mahjoub').first()
        if not admin:
            admin = AdminUser(username='ali_mahjoub', role='Owner')
            admin.set_password('123')
            db.session.add(admin)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع حساب المالك (ali_mahjoub) بنجاح.")
        else:
            print("ℹ️ [الزراعة]: حساب المالك موجود مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المالك]: {e}")

    # ============================================================
    # 2. زراعة موظف إدارة (Admin Staff)
    # ============================================================
    try:
        staff = AdminStaff.query.filter_by(username='admin_staff_test').first()
        if not staff:
            staff = AdminStaff(
                username='admin_staff_test',
                name='موظف الإدارة التجريبي',
                email='admin_staff@mahjoub.online',
                role_title='مشرف عام الإدارة',
                is_active=True,
                permissions={
                    'manage_staff': True,
                    'manage_suppliers': True,
                    'manage_products': True,
                    'manage_orders': True,
                    'view_reports': True
                }
            )
            staff.set_password('123')
            db.session.add(staff)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع موظف الإدارة التجريبي (admin_staff_test) بنجاح.")
        else:
            print("ℹ️ [الزراعة]: موظف الإدارة موجود مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة موظف الإدارة]: {e}")

    # ============================================================
    # 3. زراعة مورد تجريبي مع محفظة ورصيد افتتاحي وسند خزينة
    # ============================================================
    try:
        supplier = Supplier.query.filter_by(username='test_supplier').first()
        if not supplier:
            supplier = Supplier(
                username='test_supplier',
                trade_name='متجر محجوب التجريبي',
                owner_name='المورد التجريبي',
                store_name='متجر محجوب أونلاين',
                status='active'
            )
            supplier.phone = '779077746'
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()

        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        if not wallet:
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL963{supplier.id}",
                balance_sar=1000000.00,
                status='active'
            )
            db.session.add(wallet)
            db.session.flush()

        existing_tx = WalletTransaction.query.filter_by(
            wallet_id=wallet.id,
            trans_type='deposit',
            amount=1000000.00
        ).first()

        if not existing_tx:
            now = datetime.utcnow()
            date_str = now.strftime('%Y%m%d')
            time_stamp = now.strftime('%H%M%S%f')[:9]
            characters = string.ascii_uppercase + string.digits

            while True:
                random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
                candidate_ref = f"TRX-SUP9631-{date_str}-{time_stamp}-{random_6_code}"
                exists_ref = db.session.scalar(
                    select(WalletTransaction.id).where(
                        WalletTransaction.reference_number == candidate_ref
                    )
                )
                if not exists_ref:
                    seed_ref_number = candidate_ref
                    break

            seed_voucher_number = generate_unique_voucher_number(
                db.session.connection(),
                length=6,
                prefix="VCH-"
            )

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
            print("✅ [الزراعة]: تم زرع المورد والمحفظة وخزينة الرصيد الافتتاحي (1,000,000 SAR) بنجاح.")
            print(f"    📌 كود المورد: SUP-963{supplier.id}")
            print(f"    📌 كود المحفظة: WEL-963{supplier.id}")
            print(f"    📌 رقم السند: {seed_voucher_number}")
        else:
            print("ℹ️ [الزراعة]: المورد التجريبي والمحفظة ومعاملة الرصيد الافتتاحي موجودة مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المورد والمحفظة]: {e}")


def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config.from_object('config.Config')
    config.Config.validate_config()

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )

    # ============================================================
    # 🔌 إعدادات الاتصال بقاعدة البيانات
    # ============================================================
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    db.init_app(app)
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

    # ============================================================
    # ⚙️ تنظيف وتفريغ الجلسات عند انتهاء الطلب أو وقوع خطأ
    # ============================================================
    @app.teardown_request
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.remove()

    @app.errorhandler(500)
    def handle_500_error(e):
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": "حدث خطأ داخلي في الخادم"}), 500

    # ============================================================
    # ⚙️ التهيئة وإعادة بناء الجداول بالكامل عند عملية الرفع
    # ============================================================
    with app.app_context():
        import_all_models()
        try:
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()
            print("✅ [إعادة البناء الكامل]: تم حذف جميع الجداول القديمة وإعادة تعيين الـ Schema بنجاح.")

            db.create_all()
            print("✅ [إنشاء الجداول]: تم إنشاء جميع الجداول بنجاح.")

            seed_database()
            print("✅ [الزراعة التلقائية]: تمت زراعة البيانات المبدئية بنجاح.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ [خطأ في إعادة بناء الجداول]: {e}")

    # ============================================================
    # ⚙️ أمر CLI لإعادة بناء القاعدة يدوياً
    # ============================================================
    @app.cli.command("rebuild-db")
    def rebuild_db_command():
        """حذف جميع الجداول وإعادة إنشائها وزراعة البيانات المبدئية عبر السطر البرمجي."""
        click.echo("🔄 [إعادة بناء القاعدة]: جاري حذف جميع الجداول...")
        import_all_models()
        try:
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()
            click.echo("✅ [إعادة تعيين الـ Schema]: تم مسح وإعادة إنشاء الـ Schema بنجاح (CASCADE).")
        except Exception as e:
            db.session.rollback()
            click.echo(f"❌ [خطأ إعادة تعيين الـ Schema]: {e}")

        click.echo("⚙️ [إعادة بناء القاعدة]: جاري إنشاء الجداول بالهيكل الجديد...")
        db.create_all()
        click.echo("✅ [إنشاء الجداول]: تم إنشاء جميع الجداول بنجاح.")

        click.echo("🌱 [إعادة بناء القاعدة]: جاري زراعة البيانات المبدئية وتوثيق السندات...")
        seed_database()
        click.echo("🎉 [إعادة بناء القاعدة]: اكتملت عملية إعادة البناء والتسجيل بنجاح!")

    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    from apps.extensions import csrf, limiter
    csrf.init_app(app)
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

        try:
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
        except Exception as e:
            db.session.rollback()
            print(f"❌ [خطأ تحميل المستخدم load_user]: {e}")
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')
        # ✅ لا تعيد التوجيه لصفحات تسجيل الدخول
        if request.path.startswith('/supplier') or request.path.startswith('/suppliers'):
            return redirect(url_for('suppliers_auth_bp.login'))
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

        # ✅ إضافة جميع مسارات المصادقة هنا لمنع التوجيه اللانهائي
        exempt_prefixes = [
            '/static',
            '/graphql',
            '/admin/graphql',
            '/favicon.ico',
            '/m7jb_test_connection',
            '/supplier/login',
            '/supplier/register',
            '/supplier/forgot-password',
            '/supplier/forgot-password-page',
            '/supplier/verify-page',
            '/supplier/reset-password',
            '/suppliers/login',
            '/suppliers/register',
            '/suppliers/forgot-password',
            '/suppliers/forgot-password-page',
            '/suppliers/verify-page',
            '/suppliers/reset-password',
            admin_login_path,
            '/auth',
            '/whatsapp'
        ]

        # ✅ التحقق من المسار بشكل دقيق
        if path == '/' or any(path == p or path.startswith(p + '/') for p in exempt_prefixes):
            return

        if current_user.is_authenticated:
            is_admin_side = isinstance(current_user, (AdminUser, AdminStaff))
            is_supplier_side = isinstance(current_user, (Supplier, SupplierStaff))

            if path.startswith('/admin') or path.startswith('/dashboard'):
                if is_admin_side:
                    return
                if is_supplier_side:
                    return redirect('/supplier/dashboard')
                return redirect(admin_login_path)

            if path.startswith('/supplier') or path.startswith('/suppliers'):
                if is_supplier_side:
                    return
                if is_admin_side:
                    return redirect('/dashboard')
                return redirect(url_for('suppliers_auth_bp.login'))

            return

        # ✅ إذا لم يكن المستخدم مصادقاً وكان المسار يبدأ بـ /supplier أو /suppliers
        # لا تفعل شيئاً (تم التعامل معه في exempt)
        if path.startswith('/supplier') or path.startswith('/suppliers'):
            return

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

    # ============================================================
    # ✅ التوجيهات
    # ============================================================
    @app.route('/suppliers/login', methods=['GET', 'POST'])
    def suppliers_login_redirect_alias():
        return redirect(url_for('suppliers_auth_bp.login', **request.args))

    @app.route('/suppliers/register', methods=['GET', 'POST'])
    def suppliers_register_redirect_alias():
        return redirect(url_for('suppliers_auth_bp.register_page', **request.args))

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

    @app.route('/auth/m7jb_sovereign_hq_v2_99x')
    def deceptive_admin_honeypot():
        from flask import render_template
        try:
            return render_template('auth/deceptive_login.html')
        except Exception:
            return "<h1>401 Unauthorized</h1><p>Access Denied to Sovereign HQ.</p>", 401

    @app.route('/')
    def index():
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff

        admin_login_path = os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x')

        if current_user.is_authenticated:
            if isinstance(current_user, (Supplier, SupplierStaff)):
                return redirect('/supplier/dashboard')
            elif isinstance(current_user, (AdminUser, AdminStaff)):
                return redirect('/dashboard')
            return redirect(admin_login_path)

        return redirect(admin_login_path)

    # ============================================================
    # 🗂️ تسجيل البوابات والموديولات
    # ============================================================
    try:
        from apps.auth_portal.routes import auth_portal
        app.register_blueprint(auth_portal)
        print("✅ [بوابة المصادقة]: تم تسجيل بوابة المصادقة الإدارية بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ بوابة المصادقة]: فشل تسجيل بوابة المصادقة الإدارية: {e}")

    try:
        from apps.suppliers_auth_portal.routes import suppliers_auth_bp
        app.register_blueprint(suppliers_auth_bp, url_prefix='/suppliers')
        csrf.exempt(suppliers_auth_bp)
        print("✅ [بوابة الموردين]: تم تسجيل بوابة الموردين بنجاح.")
    except Exception as e:
        print(f"❌ [خطأ بوابة الموردين]: فشل تسجيل بوابة الموردين: {e}")

    try:
        from apps.admin.graphql_routes import graphql_bp
        app.register_blueprint(graphql_bp)
        csrf.exempt(graphql_bp)
        print("✅ [مسارات GraphQL]: تم تسجيل مسارات GraphQL الإدارية بنجاح.")
    except ImportError:
        pass
    except Exception as e:
        print(f"❌ [خطأ مسارات GraphQL]: {e}")

    try:
        from apps.whatsapp_service.routes import webhook_public_bp, whatsapp_bp

        if webhook_public_bp.name not in app.blueprints:
            app.register_blueprint(webhook_public_bp)
            print("✅ [واتساب]: تم تسجيل مسار الـ Webhook العام '/whatsapp/webhook' بنجاح.")

        if whatsapp_bp.name not in app.blueprints:
            app.register_blueprint(whatsapp_bp)
            print("✅ [واتساب]: تم تسجيل مسارات لوحة التحكم '/admin/whatsapp' بنجاح.")

        csrf.exempt(whatsapp_bp)
        csrf.exempt(webhook_public_bp)

    except Exception as e:
        print(f"❌ [خطأ واتساب]: فشل تسجيل المسار العام: {e}")

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
                        print(f"🟢 [التسجيل الديناميكي]: ✅ تم تحميل وتسجيل الموديول '{item}' بنجاح.")
                except Exception as e:
                    print(f"❌ [خطأ التسجيل الديناميكي]: فشل تسجيل موديول '{item}' - السبب: {e}")

    @app.context_processor
    def inject_vars():
        def safe_url_for(endpoint, **values):
            try:
                return url_for(endpoint, **values)
            except Exception:
                return '#'

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
                db.session.rollback()
                print(f"⚠️ [خطأ معالج السياق Context Processor]: {e}")

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
