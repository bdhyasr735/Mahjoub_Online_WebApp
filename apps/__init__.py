# 📂 apps/__init__.py
import os
import sys
import random
from flask import Flask
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash

# إعداد المسارات
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path: 
    sys.path.insert(0, base_dir)

from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# مفتاح إيقاف النظام - للتحكم الكامل
SYSTEM_ONLINE = True 

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # حماية: التحقق من حالة النظام
    @app.before_request
    def check_maintenance():
        if not SYSTEM_ONLINE:
            return "المنصة في فترة حداد مؤقتة، نعود قريباً.", 503

    # الإعدادات الأساسية
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 🛡️ إضافات الأمان (يجب أن يكون flask-talisman و flask-limiter في requirements.txt)
    Talisman(app, content_security_policy=None)
    limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

    # تهيئة الإضافات
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
    from apps.financial_ops.routes import financial_blueprint
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.wallet.routes import wallet_app

    app.register_blueprint(auth_portal, url_prefix='')
    app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(financial_blueprint, url_prefix='/financial_ops')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(wallet_app, url_prefix='/wallet')

    # 🏭 تشغيل المصنع (تهيئة قاعدة البيانات)
    with app.app_context():
        db.create_all()
        try:
            if not AdminUser.query.first():
                admin = AdminUser(username='علي_محجوب', role='Owner', phone_number='0000000000')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()

            if not Supplier.query.first():
                for i in range(1, 22):
                    new_sup = Supplier(
                        username=f'sup_{i}', 
                        password_hash=generate_password_hash('sup_pass_123'),
                        status='نشط', rank_grade='ريادي', 
                        trade_name=f'مؤسسة المورد {i}', owner_name=f'المالك {i}', 
                        wallet_code=f'W-{i}-2026', owner_phone=f'7700000{i:02d}'
                    )
                    db.session.add(new_sup)
                    db.session.flush()
                    
                    new_wallet = SupplierWallet(
                        supplier_id=new_sup.id, 
                        balance_usd=round(random.uniform(100, 5000), 2),
                        balance_sar=round(random.uniform(500, 10000), 2),
                        balance_yer=round(random.uniform(10000, 500000), 2)
                    )
                    db.session.add(new_wallet)
                db.session.commit()
                print("✅ [المصنع] تم بناء البيانات بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [المصنع] خطأ: {e}")

    return app
