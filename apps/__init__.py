# 📂 apps/__init__.py - المصنع المحصن (النسخة النهائية المصححة)

import os
from flask import Flask
from flask_talisman import Talisman
from config import Config
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models.order_db import Order
from flask_login import login_required

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', instance_relative_config=True)
    app.config.from_object(Config)

    # 🛡️ سياسة أمان المحتوى (CSP)
    csp_policy = {
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net", "https://code.jquery.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https://*"]
    }
    
    Talisman(app, force_https=False, content_security_policy=csp_policy, 
             frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # استيراد الـ Blueprints
    from apps.auth_portal.routes import auth_portal
    from apps.add_supplier.routes import add_supplier_bp
    from apps.admin_dashboard.routes import admin_dashboard
    from apps.wallet.routes import wallet_app
    from apps.vault.routes import vault_bp
    from apps.mahjoub_bridge.routes import bridge_bp
    from apps.orders.routes import orders_bp

    # تطبيق الحماية للطلبات قبل التسجيل لتجنب الخطأ
    @orders_bp.before_request
    @login_required
    def require_login():
        pass

    # تسجيل المسارات
    app.register_blueprint(auth_portal, url_prefix='/')
    app.register_blueprint(add_supplier_bp, url_prefix='/suppliers')
    app.register_blueprint(admin_dashboard, url_prefix='/admin')
    app.register_blueprint(wallet_app, url_prefix='/wallet')
    app.register_blueprint(vault_bp, url_prefix='/vault')
    app.register_blueprint(bridge_bp, url_prefix='/bridge')
    app.register_blueprint(orders_bp, url_prefix='/orders')

    # إعداد البيانات التأسيسية
    with app.app_context():
        try:
            db.create_all() 
            if not AdminUser.query.filter_by(username='علي_محجوب').first():
                admin = AdminUser(username='علي_محجوب', role='Owner', phone_number='0000000000')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
            print("✅ تم التأسيس بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ: {e}")

    return app
