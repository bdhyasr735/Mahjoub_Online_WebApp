# coding: utf-8
# 📂 apps/__init__.py - المصنع الاحترافي الشامل (حل مشكلة استيراد الكوفينج نهائياً)

import os
import sys
import traceback
from datetime import timedelta
from flask import Flask, redirect

# تهيئة الإضافات في النطاق العام (بدون استيراد Config هنا لضمان سلامة الرفع والـ Build)
from apps.extensions import db, login_manager, migrate
from werkzeug.middleware.proxy_fix import ProxyFix

def safe_register(app_instance, module_path, attr_name, prefix):
    """تسجيل المسارات (Blueprints) مع معالجة الأخطاء الذكية."""
    try:
        module = __import__(module_path, fromlist=[attr_name])
        blueprint = getattr(module, attr_name)
        app_instance.register_blueprint(blueprint, url_prefix=prefix)
        print(f"✅ Registered: {module_path}")
    except Exception as e:
        print(f"⚠️ Security Alert: Failed to register {attr_name} - Error: {e}")

def create_app():
    app = Flask(__name__)
    
    # --- الحل السحري: إضافة مسار الجذر واستيراد الكوفينج داخل الدالة لتجنب أخطاء بيئات GitHub و Render ---
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    
    try:
        from config import Config
        app.config.from_object(Config)
        print("✅ Config loaded safely inside create_app.")
    except ImportError:
        print("⚠️ Warning: Config file not found, applying env variables directly.")
        # حماية احتياطية للسيرفر إذا تم قراءته في بيئة اختبارية أو سحابية بدون ملف
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-emergency-key')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///emergency.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # إعدادات الأمان الصارمة للجلسات
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_HTTPONLY'] = True  
    app.config['SESSION_COOKIE_SECURE'] = True    
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # إعدادات الاتصال لقاعدة البيانات لمنع الانقطاع المفاجئ (Database Connection Pool)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # التوافق الكامل مع خوادم معالجة البروكسي والـ SSL في Render
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # تهيئة الإضافات الأساسية بربطها بالتطبيق الحالي
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # استيراد النماذج (Models) لضمان تسجيلها داخل نظام الـ ORM
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction
        from apps.models.vault_db import AdminVault, VaultTransaction
        
        @login_manager.user_loader
        def load_user(user_id):
            return AdminUser.query.get(int(user_id))

        # تسجيل المسارات (Blueprints)
        safe_register(app, 'apps.auth_portal.routes', 'auth_portal', '')
        safe_register(app, 'apps.add_supplier.routes', 'add_supplier_bp', '/suppliers')
        safe_register(app, 'apps.financial_ops.routes', 'financial_blueprint', '/financial_ops')
        safe_register(app, 'apps.admin_dashboard.routes', 'admin_dashboard', '/admin')
        safe_register(app, 'apps.api.search', 'api_search', '/api')
        safe_register(app, 'apps.wallet.routes', 'wallet_app', '/wallet')

        # --- درع حماية السيرفر من الانهيار الكلي عند الأخطاء المفاجئة ---
        @app.errorhandler(Exception)
        def handle_global_error(e):
            print("🚨 التقط درع الأمان خطأ غير متوقع - السيرفر لم ينهار ولن يفصل:")
            print(traceback.format_exc())
            return "عذراً، حدث خطأ مؤقت في هذا الجزء. النظام لا يزال يعمل ومستقر تماماً.", 500

        # --- مسار النبض لمنع Render من تحويل السيرفر لحالة السبات (Spin-down) ---
        @app.route('/health')
        def health_check():
            return "System Status: Online and Active", 200

        @app.route('/robots.txt')
        def robots_txt():
            return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

        @app.route('/')
        def root_redirect():
            return redirect('/login')

        @app.after_request
        def add_security_headers(response):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers.pop("Server", None)
            return response

    return app
