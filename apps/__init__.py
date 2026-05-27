# coding: utf-8
# 🏗️ مصنع التطبيق المركزي (Application Factory) - منصة محجوب أونلاين 2026

import os
from flask import Flask
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 🔐 تهيئة التشفير بشكل آمن (تجنب الانهيار إذا كان المفتاح غير موجود)
    try:
        from apps.utils.security import cipher_suite
        app.cipher = cipher_suite
        print("✅ تم تحميل نظام التشفير وتأمينه بنجاح.")
    except Exception as e:
        print(f"⚠️ تحذير: فشل تحميل نظام التشفير، قد تكون البيانات غير قابلة للقراءة: {e}")

    # تحسينات الاستقرار في بيئة الإنتاج (مهم لـ Railway)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # ربط الامتدادات بالتطبيق
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_portal.login'

    # استخدام app_context لضمان تحميل الموديلات والمسارات بأمان
    with app.app_context():
        try:
            # 1. استيراد الموديلات
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            from apps.models.settlements_db import AdminSettlement
            from apps.models.statement_db import SupplierStatement 
            
            # 2. إنشاء الجداول (معالجة الأخطاء هنا تمنع انهيار المصنع)
            db.create_all() 

            # 3. إعداد إدارة المستخدمين
            @login_manager.user_loader
            def load_user(user_id):
                return AdminUser.query.get(int(user_id))

            # 4. استيراد وتسجيل البلوبرينتس (Blueprints)
            from apps.auth_portal.routes import auth_blueprint
            from apps.admin_dashboard.routes import admin_dashboard
            from apps.add_supplier.routes import admin_suppliers_bp
            from apps.financial_ops.routes import financial_blueprint 
            from apps.statement.routes import statement_blueprint

            app.register_blueprint(auth_blueprint, url_prefix='/auth')
            app.register_blueprint(admin_dashboard)
            app.register_blueprint(admin_suppliers_bp, url_prefix='/suppliers')
            app.register_blueprint(financial_blueprint, url_prefix='/finance')
            app.register_blueprint(statement_blueprint, url_prefix='/statement')
            
            print("✅ تم تسجيل جميع البلوبرينتس بنجاح.")

        except Exception as e:
            print(f"❌ خطأ فادح أثناء تهيئة التطبيق: {e}")
            # نترك التطبيق يستمر في العمل (قد يظهر أخطاء ولكن لن ينهار تماماً)

    return app
