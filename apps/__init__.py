# coding: utf-8
# 📂 apps/__init__.py - المصنع السيادي للإدارة (نسخة معزولة تماماً)

import os
import importlib
from flask import Flask, redirect, url_for
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

    # 2. 🛡️ سياسة أمان المحتوى (CSP)
    Talisman(app, force_https=True, content_security_policy={
        'default-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "data:", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"],
        'img-src': ["'self'", "data:", "https://*"]
    }, frame_options='SAMEORIGIN', referrer_policy='strict-origin-when-cross-origin')

    # 3. تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    @login_manager.user_loader
    def load_user(user_id):
        from apps.models.admin_db import AdminUser
        return AdminUser.query.get(int(user_id))

    # 4. تسجيل مسارات الإدارة فقط (بدون أي استيراد للموردين هنا)
    core_blueprints = [
        ('apps.auth_portal.routes', 'auth_portal', '/auth'),
        ('apps.admin_dashboard.routes', 'admin_dashboard', '/admin'),
        ('apps.wallet.routes', 'wallet_app', '/wallet'),
        ('apps.vault.routes', 'vault_bp', '/vault'),
        ('apps.orders.routes', 'orders_bp', '/orders'),
        ('apps.api.webhooks', 'webhooks_bp', '/api')
    ]

    for module_path, bp_name, prefix in core_blueprints:
        try:
            module = importlib.import_module(module_path)
            app.register_blueprint(getattr(module, bp_name), url_prefix=prefix)
        except ImportError as e:
            print(f"🚨 [System] خطأ في تحميل مسار الإدارة {bp_name}: {e}")

    # 5. عزل تام: الموردون لا يُسجلون في هذا المصنع إلا عبر الـ Registry الديناميكي
    # الميزة: لو انهار الموردون، لن تتأثر الإدارة لأنهم لا يستوردون في `try` أعلاه
    apps_dir = os.path.dirname(__file__)
    for folder in os.listdir(apps_dir):
        # تجاهل أي شيء ليس جزءاً من الإدارة إذا أردت عزلهم تماماً
        if folder in {'suppliers_auth_portal', 'suppliers_dashboard'}:
            registry_path = os.path.join(apps_dir, folder, 'registry.py')
            if os.path.exists(registry_path):
