# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask
from apps.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        # 1. استيراد الموديلات لتسجيل الجداول في SQLAlchemy
        import apps.models
        
        # 2. [التعديل]: بناء الجداول تلقائياً إذا لم تكن موجودة
        try:
            db.create_all()
            print("✅ [Database]: تم فحص وبناء الجداول بنجاح.")
        except Exception as e:
            print(f"⚠️ [Database]: خطأ أثناء محاولة بناء الجداول: {e}")
        
        # 3. --- نظام الاكتشاف التلقائي (Auto-Discovery) ---
        apps_dir = app.root_path
        
        # البحث في جميع المجلدات داخل apps
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            # استثناء المجلدات غير الموديولية
            if item in ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations']:
                continue

            registry_file = os.path.join(item_path, 'registry.py')
            
            if os.path.isdir(item_path) and os.path.exists(registry_file):
                try:
                    module_path = f"apps.{item}.registry"
                    module = importlib.import_module(module_path)
                    
                    if hasattr(module, 'register_module'):
                        module.register_module(app)
                        print(f"✅ [Auto-Discovery] تم تسجيل الموديول: {item}")
                except Exception as e:
                    print(f"⚠️ [Auto-Discovery] فشل تسجيل {item}: {e}")

        # 4. تثبيت الـ Mappers بعد تسجيل الموديلات والـ Blueprints
        db.configure_mappers()

    return app
