# coding: utf-8
# 🏢 المصنع المركزي للنواة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# تهيئة الإضافات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    # ضمان إعداد مسار الرفع
    if not app.config.get('UPLOAD_FOLDER'):
        app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads', 'identities')

    # تهيئة الإضافات داخل المصنع
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # --- استيراد الموديلات ---
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet
        
        # إنشاء الجداول وتطبيق التعديلات البرمجية
        try:
            db.create_all()
            
            # أوامر التطهير وإعادة الهيكلة الرقمية
            commands = [
                "ALTER TABLE supplier_wallets DROP CONSTRAINT IF EXISTS supplier_wallets_supplier_id_fkey;",
                "ALTER TABLE supplier_wallets ALTER COLUMN supplier_id TYPE VARCHAR(50);",
                "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wallet_code VARCHAR(50) UNIQUE;",
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'نشطة';",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS yer_available;",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS sar_available;",
                "ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS usd_available;"
            ]
            
            for cmd in commands:
                try:
                    db.session.execute(db.text(cmd))
                except Exception:
                    continue 
            
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم إقرار البنية الرقمية للمحافظ بنجاح.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ تعذر تحديث الجداول برمجياً: {str(e)}")

    # إعدادات تسجيل الدخول
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # --- استيراد وتسجيل المسارات (Blueprints) ---
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # تسجيل المسارات مع التأكد من الأسماء المطابقة للـ url_for
    app.register_blueprint(auth_blueprint, url_prefix='/auth', name='auth_portal')
    app.register_blueprint(admin_dashboard, url_prefix='/admin', name='admin_dashboard')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers', name='add_supplier')
    app.register_blueprint(admin_wallet, url_prefix='/admin/wallet', name='admin_wallet')
    
    # معالجة الأخطاء السيادية
    @app.errorhandler(500)
    def internal_error(e):
        return f"حدث خطأ سيادي (500): {str(e)}", 500

    print("✅ تم تعميد كافة المسارات السيادية (Blueprints) بنجاح.")
    return app
