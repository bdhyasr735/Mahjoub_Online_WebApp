# coding: utf-8
# 🏢 المصنع المركزي للنواة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        import apps.models.admin_db
        import apps.models.supplier_db
        import apps.models.wallet_db
        
        try:
            db.create_all()
            # أوامر التطهير وإعادة الهيكلة الرقمية
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP CONSTRAINT IF EXISTS supplier_wallets_supplier_id_fkey;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets ALTER COLUMN supplier_id TYPE VARCHAR(50);"))
            db.session.execute(db.text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wallet_code VARCHAR(50) UNIQUE;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'نشطة';"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS yer_available;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS sar_available;"))
            db.session.execute(db.text("ALTER TABLE supplier_wallets DROP COLUMN IF EXISTS usd_available;"))
            db.session.execute(db.text("""
                ALTER TABLE supplier_wallets 
                ADD CONSTRAINT supplier_wallets_supplier_id_fkey 
                FOREIGN KEY (supplier_id) REFERENCES suppliers(sovereign_id);
            """))
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم تطهير حقول الموازين الثابتة وإقرار البنية الرقمية النصية للمحافظ بنجاح.")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ تعذر تحديث الجداول برمجياً: {str(e)}")
        finally:
            db.session.close()

    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # --- استيراد المسارات (Blueprints) ---
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # --- تسجيل الـ Blueprints ---
    app.register_blueprint(auth_blueprint, url_prefix='/auth', name='auth_portal')
    app.register_blueprint(admin_dashboard, url_prefix='/admin', name='admin_dashboard')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/admin', name='add_supplier')
    app.register_blueprint(admin_wallet, url_prefix='/admin', name='admin_wallet')
    
    print("✅ تم تعميد كافة المسارات السيادية (Blueprints) بنجاح في المصنع المركزي.")

    return app
