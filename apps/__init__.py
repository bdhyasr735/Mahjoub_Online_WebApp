# coding: utf-8
# 🏢 المصنع المركزي للنواة - منصة محجوب أونلاين 2026

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# إنشاء الكائنات المركزية كنسخ مستقلة لمنع التعارض الدائري
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # تعيين مجلد القوالب العام كخلفية احتياطية للتطبيق كاملاً
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # 🛡️ التحديث السيادي لعام 2026: حل مشكلة تشفير النصوص العربية
    app.json.ensure_ascii = False

    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)

    # 🛡️ استدعاء النماذج الحوكمة وتهيئة قاعدة البيانات
    with app.app_context():
        import apps.models.admin_db
        import apps.models.supplier_db
        import apps.models.wallet_db
        
        try:
            db.create_all()
            # 🎯 محرك التصحيح التلقائي السيادي للهيكل المالي
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
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ تعذر توليد أو تحديث الجداول برمجياً: {str(e)}")
        finally:
            db.session.close()

    # 🛡️ الحماية السيادية و Flask-Login
    login_manager.login_view = 'auth_portal.login'
    login_manager.login_message = 'يرجى إثبات الهوية الرقمية للوصول إلى المنطقة السيادية.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 📥 استيراد البلوبرينتس (تم تحديث الاستيراد للداشبورد ليطابق التعديل)
    from apps.auth_portal import auth_blueprint
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.add_supplier.routes import admin_suppliers_bp
    from apps.wallet.routes import admin_wallet

    # ⚙️ تسجيل البلوبرينتس
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    
    # تسجيل الموردين والمحافظ (بناءً على طلبك السابق بدون url_prefix مكرر إذا لزم الأمر، 
    # ولكن للتنظيم يفضل تركه كما كان إذا كان يعمل لديك سابقاً)
    app.register_blueprint(admin_suppliers_bp)
    app.register_blueprint(admin_wallet)

    return app
