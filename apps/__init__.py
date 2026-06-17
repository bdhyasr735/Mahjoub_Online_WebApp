# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي للنظام (النسخة النهائية)

from flask import Flask
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    # 1. إعداد المصنع
    app = Flask(__name__, template_folder='templates', static_folder='static', instance_relative_config=True)
    app.config.from_object(Config)

    # 2. 🛡️ سياسة أمان المحتوى (CSP)
    csp_policy = {
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https://*"]
    }
    Talisman(app, force_https=True, content_security_policy=csp_policy,
             frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

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
    from apps.orders.routes import orders_blueprint

    app.register_blueprint(auth_portal, url_prefix='/')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(wallet_app, url_prefix='/wallet')
    app.register_blueprint(vault_bp, url_prefix='/vault')
    app.register_blueprint(orders_blueprint, url_prefix='/orders')

    # 5. إعداد البيانات التأسيسية وهيكلة الجداول ذاتياً
    with app.app_context():
        try:
            # استيراد النماذج لضمان تسجيلها في SQLAlchemy
            from apps.models.admin_db import AdminUser
            from apps.models.orders_db import ProcessedOrder
            from apps.models.sync_log import SyncLog
            from apps.models.financial_db import ExchangeRate, FinancialLog
            from apps.models.supplier_db import Supplier
            from apps.models.vault_db import AdminVault, VaultTransaction
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            
            # إنشاء الجداول تلقائياً (بناءً على طلبك لعدم الحاجة للطرفية)
            db.create_all() 
            
            # تأسيس المسؤول الأول (المدير السيادي)
            if not AdminUser.query.filter_by(username='علي_محجوب').first():
                admin = AdminUser(username='علي_محجوب', role='Owner', phone_number='0000000000')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ [System] تم تأسيس الهيكل وقاعدة البيانات بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Error] خطأ أثناء التأسيس الذاتي: {e}")

    return app
