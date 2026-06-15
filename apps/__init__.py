# coding: utf-8
# 📂 apps/__init__.py - المصنع المحصن (النسخة النهائية الكاملة)

from flask import Flask
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.financial_db import ExchangeRate
from apps.models.vault_db import AdminVault
from apps.models.product_db import Product  # الموديل الموحد للمنتجات
from apps.models.order_db import Order      # الموديل الموحد للطلبات
from apps.utils.security import AESCipher
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', instance_relative_config=True)
    app.config.from_object(Config)

    # 🛡️ سياسة أمان المحتوى (CSP)
    csp_policy = {
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https://*"]
    }
    
    Talisman(app, force_https=True, content_security_policy=csp_policy,
             frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # تسجيل المسارات (Blueprints)
    from apps.auth_portal.routes import auth_portal
    from apps.add_supplier.routes import add_supplier_bp
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.wallet.routes import wallet_app
    from apps.vault.routes import vault_bp
    from apps.mahjoub_bridge.routes import products_bp  # مسار المنتجات
    from apps.orders.routes import orders_bp            # مسار الطلبات

    app.register_blueprint(auth_portal, url_prefix='/')
    app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(wallet_app, url_prefix='/wallet')
    app.register_blueprint(vault_bp, url_prefix='/vault')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')

    # إعداد البيانات التأسيسية
    with app.app_context():
        try:
            db.create_all() 
            
            # 1. إنشاء المدير
            if not AdminUser.query.filter_by(username='علي_محجوب').first():
                admin = AdminUser(username='علي_محجوب', role='Owner', phone_number='0000000000')
                admin.set_password('123')
                db.session.add(admin)
            
            # 2. زرع المتاجر والمحافظ (إذا كانت قاعدة البيانات فارغة)
            if not Supplier.query.first():
                for i in range(1, 22):
                    s = Supplier(username=f'supplier_{i}', trade_name=f'متجر رقم {i}', owner_name=f'المالك {i}')
                    s.password_hash = generate_password_hash('123')
                    db.session.add(s)
                    db.session.flush() 
                    w = SupplierWallet(
                        supplier_id=s.id,
                        _balance_sar=AESCipher.encrypt("500.0"),
                        _balance_yer=AESCipher.encrypt("0.0"),
                        _balance_usd=AESCipher.encrypt("0.0")
                    )
                    db.session.add(w)
            
            # 3. الخزينة وأسعار الصرف
            if not AdminVault.query.first():
                db.session.add(AdminVault(name="الخزنة المركزية", balance_sar=10000))
            
            if not ExchangeRate.query.first():
                db.session.add(ExchangeRate(currency_code='USD', rate_to_sar=3.75))
                db.session.add(ExchangeRate(currency_code='YER', rate_to_sar=0.004))
            
            db.session.commit()
            print("✅ تم تأسيس النظام بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ أثناء التأسيس: {e}")

    return app
