# coding: utf-8
# 🏢 المصنع المركزي للنواة المستقرة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# تهيئة الإضافات الأساسية
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    # 1. ضمان وجود مسار الأرشفة السيادية
    upload_path = os.path.join(os.getcwd(), 'uploads', 'identities')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    app.config['UPLOAD_FOLDER'] = upload_path

    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # استيراد الموديلات الأساسية
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet 
        
        # إنشاء الجداول وتحديث البنية
        try:
            db.create_all()
            
            # أوامر التطهير (SQL Hardening)
            commands = [
                "ALTER TABLE supplier_wallets DROP CONSTRAINT IF EXISTS supplier_wallets_supplier_id_fkey;",
                "ALTER TABLE supplier_wallets ALTER COLUMN supplier_id TYPE VARCHAR(50);",
                "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wallet_code VARCHAR(50) UNIQUE;",
                "ALTER TABLE supplier_wallets ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'نشطة';"
            ]
            
            for cmd in commands:
                try:
                    db.session.execute(db.text(cmd))
                except:
                    continue
            db.session.commit()
            print("🚀 سيادة وحوكمة: تم إقرار البنية الرقمية بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ في تحديث الجداول: {e}")

    # إعدادات جلسة الدخول
    login_manager.login_view = 'auth_portal.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # --- 🔄 التسجيل الآمن للحزم (Blueprints) ---
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard import admin_dashboard_bp
    from apps.add_supplier import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet 

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(admin_wallet, url_prefix='/admin/wallet')
    
    return app
