# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي للنظام

import os
import importlib
from flask import Flask, redirect, url_for
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    # 1. إعداد المصنع
    app = Flask(__name__, template_folder='templates', static_folder='static', instance_relative_config=True)
    app.config.from_object(Config)

    # 2. 🛡️ سياسة أمان المحتوى (CSP)
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
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل المسارات (Blueprints)
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

    # 5. المحرك التلقائي لاكتشاف التطبيقات
    apps_dir = os.path.dirname(__file__)
    for folder in os.listdir(apps_dir):
        folder_path = os.path.join(apps_dir, folder)
        if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, 'registry.py')):
            try:
                module = importlib.import_module(f'apps.{folder}.registry')
                if hasattr(module, 'register_app'):
                    module.register_app(app)
            except Exception as e:
                print(f"⚠️ [System] فشل تحميل {folder}: {e}")

    @app.route('/')
    def index():
        return redirect(url_for('auth_portal.login'))

    # 6. إعداد البيانات والجداول
    with app.app_context():
        try:
            from apps.models.admin_db import AdminUser
            from apps.models.admin_staff_db import AdminStaff
            from apps.models.financials_db import OrderFinancial
            from apps.models.marketers_db import Marketer
            from apps.models.orders_db import Order
            from apps.models.otp_db import OTPVerification
            from apps.models.supplier_db import Supplier
            from apps.models.supplier_profile_db import SupplierProfile
            from apps.models.supplier_staff_db import SupplierStaff
            from apps.models.sync_log import SyncLog
            # تم تصحيح الاسم هنا ليطابق الكلاس في ملف wallet_db.py
            from apps.models.wallet_db import VendorWallet

            db.create_all()
            
            # تأسيس المالك
            owner_username = 'علي محجوب'
            if not AdminUser.query.filter_by(username=owner_username).first():
                admin = AdminUser(username=owner_username, role='Owner', phone_number='0000000000')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ [System] تم تأسيس حساب المالك بنجاح.")
        except Exception as e:
            print(f"⚠️ [Error] فشل في تهيئة قاعدة البيانات: {e}")

    return app
