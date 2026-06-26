# coding: utf-8
import os
import importlib
from flask import Flask
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        # 1. بناء الجداول تلقائياً
        try:
            db.create_all()
            print("✅ [Database]: تم فحص وبناء الجداول بنجاح.")
        except Exception as e:
            print(f"⚠️ [Database]: خطأ أثناء محاولة بناء الجداول: {e}")

        # 2. إنشاء المستخدم "علي" تلقائياً
        try:
            if not AdminUser.query.filter_by(username='علي').first():
                admin = AdminUser(username='علي', role='Owner')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ [Admin]: تم إنشاء المستخدم 'علي' بنجاح.")
        except Exception as e:
            print(f"⚠️ [Admin]: خطأ أثناء إنشاء المستخدم: {e}")
        
        # 3. --- نظام الاكتشاف التلقائي (Auto-Discovery) ---
        # المسار الحالي هو مجلد 'apps'
        apps_dir = os.path.dirname(os.path.abspath(__file__))
        
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            # استبعاد المجلدات العامة وغير البرمجية
            if item in ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'auth_portal']:
                continue

            registry_file = os.path.join(item_path, 'registry.py')
            
            # التحقق من أن المجلد يحتوي على ملف registry.py
            if os.path.isdir(item_path) and os.path.exists(registry_file):
                try:
                    module_path = f"apps.{item}.registry"
                    module = importlib.import_module(module_path)
                    
                    if hasattr(module, 'register_module'):
                        module.register_module(app)
                        print(f"✅ [Auto-Discovery] تم تسجيل الموديول: {item}")
                except Exception as e:
                    print(f"⚠️ [Auto-Discovery] فشل تسجيل {item}: {e}")

        db.configure_mappers()

    return app
