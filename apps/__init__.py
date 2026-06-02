# coding: utf-8
# 🏗️ مصنع التطبيق المركزي (Application Factory) - منصة محجوب أونلاين 2026

from flask import Flask, redirect
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from apps.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 🛡️ إعداد ProxyFix (ضروري لـ Vercel لاستلام الـ Headers الصحيحة خلف الـ Reverse Proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # تهيئة الإضافات والمكتبات المركزية
    db.init_app(app)
    login_manager.init_app(app)
    
    # ⚡ تم الإصلاح أمنياً: ربط مسار الحماية بالمسمى النصي الحقيقي للبلوبرينت 'auth_portal' لمنع الـ BuildError
    login_manager.login_view = 'auth_portal.login' 

    with app.app_context():
        # دالة تسجيل آمنة لضمان استقرار المحرك وعدم انهيار السيرفر بالكامل
        def safe_register(blueprint, url_prefix=None):
            try:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                print(f"✅ تم تسجيل Blueprint بنجاح: {blueprint.name}")
            except Exception as e:
                print(f"⚠️ تحذير: فشل تسجيل {blueprint.name}: {e}")

        try:
            # 1. استيراد موديلات قاعدة البيانات لتهيئة الهيكل حركياً
            from apps.models.admin_db import AdminUser
            from apps.models.supplier_db import Supplier
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            from apps.models.settlements_db import AdminSettlement
            from apps.models.statement_db import SupplierStatement 
            
            # 🌐 تم الربط السحابي: بناء الجداول تلقائياً في قاعدة بيانات Supabase الخارجية فور الإقلاع الأول
            db.create_all() 

            @login_manager.user_loader
            def load_user(user_id):
                try:
                    return AdminUser.query.get(int(user_id))
                except Exception:
                    return None

            # 2. تسجيل الـ Blueprints والوحدات الوظيفية للنظام
            from apps.auth_portal.routes import auth_blueprint
            
            # ⚡ تم التعديل السيادي: جعل البادئة فارغة ليعمل رابط تسجيل الدخول مباشرة على النطاق الفرعي /login
            safe_register(auth_blueprint, url_prefix='')

            from apps.add_supplier.routes import add_supplier as add_supplier_bp
            safe_register(add_supplier_bp, url_prefix='/suppliers')

            from apps.financial_ops.routes import financial_blueprint
            safe_register(financial_blueprint, url_prefix='/finance')

            from apps.statement.routes import statement_blueprint
            safe_register(statement_blueprint, url_prefix='/statement')

            # تم تخصيص بادئة /admin هنا بشكل صريح لمنع تعارض المسارات مع الرابط الرئيسي
            from apps.admin_dashboard.routes import admin_dashboard
            safe_register(admin_dashboard, url_prefix='/admin')
            
            print("🚀 محرك المنصة المركزي يعمل بكفاءة واستقرار عالي مع قاعدة البيانات السحابية.")

            # 🔄 التوجيه الديناميكي الرئيسي المباشر لتغطية جذر النطاق الفرعي وتحويله فوراً لصفحة الدخول
            @app.route('/')
            def root_redirect():
                return redirect('/login')

        except Exception as e:
            print(f"❌ خطأ جسيم في تهيئة وهندسة التطبيق: {e}")

    return app
