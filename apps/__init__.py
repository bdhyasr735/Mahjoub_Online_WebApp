# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي الموحد

import os
from flask import Flask, redirect
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate

def create_app():
    # 1. إعداد المصنع
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static', 
                static_url_path='/static',
                instance_relative_config=True)
    
    app.config.from_object(Config)

    # تحسينات الأمان
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True
    )

    # 2. 🛡️ سياسة أمان المحتوى
    Talisman(app, force_https=True, content_security_policy={
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://*"]
    }, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    # 3. الإضافات الأساسية
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل المسارات (Lazy Loading لتجنب فصل السيرفر)
    with app.app_context():
        from apps.auth_portal.routes import auth_portal
        from apps.admin_dashboard.routes import admin_dashboard
        from apps.wallet.routes import wallet_app
        from apps.vault.routes import vault_bp
        from apps.orders.routes import orders_bp
        from apps.api.webhooks import webhooks_bp
        # إضافة موديول الموردين السيادي
        from apps.suppliers_auth_portal.routes import suppliers_bp

        app.register_blueprint(auth_portal, url_prefix='/auth')
        app.register_blueprint(admin_dashboard, url_prefix='/admin')
        app.register_blueprint(wallet_app, url_prefix='/wallet')
        app.register_blueprint(vault_bp, url_prefix='/vault')
        app.register_blueprint(orders_bp, url_prefix='/orders')
        app.register_blueprint(webhooks_bp, url_prefix='/api')
        # تسجيل مسار الموردين الموحد
        app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    
    print("✅ [SYSTEM] تم تسجيل كافة المسارات (بما في ذلك بوابة الموردين) بنجاح.")

    # 5. التوجيه الأساسي
    @app.route('/')
    def index():
        login_path = os.environ.get('ADMIN_LOGIN_PATH', '/m7jb_sovereign_hq_v2_99x')
        return redirect(f'/auth{login_path}')

    # 6. إعداد البيانات
    with app.app_context():
        try:
            from apps.models.admin_db import AdminUser
            db.create_all()
            if not AdminUser.query.filter_by(username='علي محجوب').first():
                admin = AdminUser(username='علي محجوب', role='Owner', phone_number='779077746')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
        except Exception as e:
            print(f"⚠️ [Database Setup] خطأ: {e}")

    return app
