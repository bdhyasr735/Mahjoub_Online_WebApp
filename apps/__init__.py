# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, redirect, session, url_for, request, jsonify, render_template
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

    CORS(app, resources={r"/admin/*": {"origins": ["https://studio.apollographql.com", "http://localhost:5000"]}}, supports_credentials=True)

    db.init_app(app)
    
    # ============================================================
    # ✅ إعادة بناء الجداول تلقائياً
    # ============================================================
    with app.app_context():
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        from apps.models.wallet_db import SupplierWallet
        from apps.models.product_supplier_map import ProductSupplierMapping
        from apps.models.admin_staff_db import AdminStaff
        
        print("🔄 [DB]: جاري إعادة ضبط وبناء الجداول...")
        db.session.execute(db.text('DROP SCHEMA public CASCADE; CREATE SCHEMA public;'))
        db.session.commit()
        db.create_all()
        print("✅ [DB]: تم إعادة إنشاء الجداول.")

        # 1. زراعة المالك (AdminUser)
        try:
            if not AdminUser.query.filter_by(username='ali_mahjoub').first():
                new_admin = AdminUser(username='ali_mahjoub', role='Owner')
                new_admin.set_password('123')
                db.session.add(new_admin)
                db.session.commit()
                print("✅ [Seed]: تم زرع المالك.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ المالك: {e}")

        # 2. زراعة موظف إدارة (AdminStaff) - تم تصحيح الحقول
        try:
            if not AdminStaff.query.filter_by(username='admin_staff_test').first():
                new_admin_staff = AdminStaff(
                    username='admin_staff_test',
                    role_title='مشرف عام',
                    is_active=True,
                    permissions={'manage_staff': True, 'manage_suppliers': True, 'manage_products': True}
                )
                new_admin_staff.set_password('123')
                db.session.add(new_admin_staff)
                db.session.commit()
                print("✅ [Seed]: تم زرع موظف الإدارة.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ موظف الإدارة: {e}")
        
        # 3. زراعة مورد تجريبي (Supplier) - تم تصحيح الحقول
        try:
            if not Supplier.query.filter_by(username='test_supplier').first():
                test_supplier = Supplier(
                    username='test_supplier',
                    trade_name='متجر تجريبي',
                    owner_name='المورد التجريبي',
                    phone='0500000000',
                    status='active'
                )
                test_supplier.set_password('123')
                db.session.add(test_supplier)
                db.session.flush() # لتوليد الـ ID
                
                wallet = SupplierWallet(
                    supplier_id=test_supplier.id,
                    wallet_code=f"MAH-WEL963{test_supplier.id}",
                    balance_sar=1000.00
                )
                db.session.add(wallet)
                db.session.commit()
                print("✅ [Seed]: تم زرع المورد والمحفظة.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ المورد: {e}")

        # 4. زراعة موظف مورد (SupplierStaff)
        try:
            supplier = Supplier.query.filter_by(username='test_supplier').first()
            if supplier and not SupplierStaff.query.filter_by(username='supplier_staff_test').first():
                new_supplier_staff = SupplierStaff(
                    supplier_id=supplier.id,
                    username='supplier_staff_test',
                    role_title='مساعد مبيعات',
                    is_active=True,
                    permissions={'manage_catalog': True, 'process_orders': True}
                )
                new_supplier_staff.set_password('123')
                db.session.add(new_supplier_staff)
                db.session.commit()
                print("✅ [Seed]: تم زرع موظف المورد.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Seed]: خطأ موظف المورد: {e}")

    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # [بقية كود الـ Flask كما هو...]
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        user_id_int = int(user_id)
        user_type = session.get('user_type')
        if user_type == 'admin': return db.session.get(AdminUser, user_id_int)
        elif user_type == 'staff': 
            staff = db.session.get(AdminStaff, user_id_int)
            return staff if staff else db.session.get(SupplierStaff, user_id_int)
        elif user_type == 'supplier': return db.session.get(Supplier, user_id_int)
        return db.session.get(Supplier, user_id_int) or db.session.get(SupplierStaff, user_id_int) or db.session.get(AdminUser, user_id_int)

    @app.route('/')
    def index():
        return redirect(os.environ.get('ADMIN_LOGIN_PATH', '/auth/m7jb_sovereign_hq_v2_99x'))

    # تسجيل البلوبرنتس والموديولات (كما في كودك الأصلي...)
    try:
        from apps.auth_portal.routes import auth_portal
        app.register_blueprint(auth_portal)
    except: pass
    try:
        from apps.suppliers_auth_portal.routes import suppliers_bp
        app.register_blueprint(suppliers_bp, url_prefix='/supplier')
        csrf.exempt(suppliers_bp)
    except: pass

    return app
