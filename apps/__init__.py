# coding: utf-8
# 📂 apps/__init__.py - المصنع المحصن (تم تفعيل إعادة بناء القاعدة)

import os
import sys
from flask import Flask
from flask_migrate import Migrate
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash
from apps.config import Config  # استيراد الإعدادات المركزية

# إعداد المسارات
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path: 
    sys.path.insert(0, base_dir)

from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.financial_db import ExchangeRate, FinancialLog
from apps.models.vault_db import AdminVault, VaultTransaction

def create_app():
    app = Flask(__name__)
    
    # تحميل الإعدادات من كلاس Config المركزي
    app.config.from_object(Config)
    
    # 🛡️ تحصين التطبيق
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "https://code.jquery.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "'unsafe-inline'"],
        'style-src': ["'self'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com", "'unsafe-inline'"],
        'font-src': ["'self'", "https://cdnjs.cloudflare.com", "https://fonts.gstatic.com"],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'"]
    }
    
    Talisman(app, content_security_policy=csp, force_https=True, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # تسجيل الـ Blueprints
    from apps.auth_portal.routes import auth_portal
    from apps.add_supplier.routes import add_supplier_bp
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.wallet.routes import wallet_app
    from apps.vault.routes import vault_bp

    app.register_blueprint(auth_portal, url_prefix='')
    app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(wallet_app, url_prefix='/wallet')
    app.register_blueprint(vault_bp, url_prefix='/vault')

    # تهيئة قاعدة البيانات وإعادة زرع البيانات التأسيسية
    with app.app_context():
        # ⚠️ تنبيه: هذا السطر سيحذف كل البيانات القديمة ويعيد بناء الجداول من الصفر
        db.drop_all() 
        db.create_all()
        
        try:
            # 1. إنشاء المدير
            admin = AdminUser(username='علي_محجوب', role='Owner', phone_number='0000000000')
            admin.set_password('123')
            db.session.add(admin)
            
            # 2. إنشاء الخزينة المركزية
            vault = AdminVault(balance_sar=0, balance_yer=0, balance_usd=0)
            db.session.add(vault)
            
            # 3. زرع أسعار الصرف
            db.session.add(ExchangeRate(currency_code='USD', rate_to_sar=3.75))
            db.session.add(ExchangeRate(currency_code='YER', rate_to_sar=0.004))
            
            # 4. زرع الموردين
            for i in range(1, 22):
                new_sup = Supplier(
                    username=f'sup_{i}', 
                    password_hash=generate_password_hash('sup_pass_123'),
                    status='قيد المراجعة', rank_grade='ريادي', 
                    trade_name=f'مؤسسة المورد {i}', owner_name=f'المالك {i}', 
                    wallet_code=f'W-{i}-2026', owner_phone=f'7700000{i:02d}'
                )
                db.session.add(new_sup)
                db.session.flush() # للحصول على الـ ID للمورد
                db.session.add(SupplierWallet(supplier_id=new_sup.id, balance_sar=0, balance_yer=0, balance_usd=0))
            
            db.session.commit()
            print("✅ تم مسح قاعدة البيانات القديمة وزرع البيانات التأسيسية المشفرة بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ أثناء التأسيس: {e}")

    return app
