# coding: utf-8
from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 🛡️ إعداد ProxyFix لضبط البروتوكولات في Render
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # تهيئة الإضافات
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # 1. تهيئة الجداول
        try:
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            from apps.models.settlements_db import AdminSettlement
            from apps.models.statement_db import SupplierStatement
            db.create_all()
            print("⚡ [Database] تم بناء الجداول بنجاح.")
        except Exception as e:
            print(f"❌ [Database Error] فشل تهيئة قاعدة البيانات: {e}")

        # 2. تهيئة user_loader
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id)) if user_id else None

        # 3. تسجيل المسارات (Blueprints) بأسلوب آمن
        blueprints = [
            ('apps.auth_portal.routes', 'auth_blueprint', ''),
            ('apps.add_supplier.routes', 'add_supplier', '/suppliers'),
            ('apps.financial_ops.routes', 'financial_blueprint', '/financial_ops'),
            ('apps.statement.routes', 'statement_blueprint', '/statement'),
            ('apps.admin_dashboard.routes', 'admin_dashboard', '/admin')
        ]

        for module_path, bp_name, prefix in blueprints:
            try:
                module = __import__(module_path, fromlist=[bp_name])
                blueprint = getattr(module, bp_name)
                app.register_blueprint(blueprint, url_prefix=prefix)
                print(f"✅ تم تسجيل {bp_name} بنجاح.")
            except Exception as e:
                print(f"⚠️ [Warning] فشل تسجيل {bp_name}، السيرفر سيستمر بالعمل: {e}")
        
        # 4. توجيه المسار الرئيسي
        @app.route('/')
        def root_redirect():
            return redirect('/login')

    return app
