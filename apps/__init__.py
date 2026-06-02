# coding: utf-8
# 🏗️ مصنع التطبيق المركزي (Application Factory) - منصة محجوب أونلاين 2026

from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 🛡️ إعداد ProxyFix (ضروري لـ Vercel لاستلام الـ Headers الصحيحة)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # ⚡ إضافة هامة: التأكد من استيراد كائن db داخل السياق لضمان الاتصال السحابي
        from apps.extensions import db
        
        # استيراد النماذج (Models) لضمان معرفة SQLAlchemy بها
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.settlements_db import AdminSettlement
        from apps.models.statement_db import SupplierStatement 
        
        # ⚡ تحديث: إنشاء الجداول والتأكد من الاتصال بـ Supabase
        try:
            db.create_all()
            print("✅ تم التحقق من سلامة قاعدة البيانات والاتصال بـ Supabase.")
        except Exception as e:
            print(f"⚠️ تنبيه قاعدة البيانات: {e}")

        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id)) if user_id else None

        # تسجيل الـ Blueprints
        def safe_register(blueprint, url_prefix=None):
            try:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
            except Exception as e:
                print(f"⚠️ فشل تسجيل {blueprint.name}: {e}")

        from apps.auth_portal.routes import auth_blueprint
        safe_register(auth_blueprint, url_prefix='')

        from apps.add_supplier.routes import add_supplier as add_supplier_bp
        safe_register(add_supplier_bp, url_prefix='/suppliers')

        from apps.financial_ops.routes import financial_blueprint
        safe_register(financial_blueprint, url_prefix='/finance')

        from apps.statement.routes import statement_blueprint
        safe_register(statement_blueprint, url_prefix='/statement')

        from apps.admin_dashboard.routes import admin_dashboard
        safe_register(admin_dashboard, url_prefix='/admin')
        
        @app.route('/')
        def root_redirect():
            return redirect('/login')

    return app
