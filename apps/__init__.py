# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from apps.extensions import db, login_manager, migrate
from apps.models import AdminUser, Supplier, SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.utils.time_utils import format_full_timestamp

# تهيئة الحماية
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    """
    دالة تحميل المستخدم التي تعتمد على نوعه المخزن في الجلسة
    """
    user_type = session.get('user_type')
    try:
        uid = int(user_id)
        if user_type == 'admin': return AdminUser.query.get(uid)
        elif user_type == 'supplier': return Supplier.query.get(uid)
        elif user_type == 'staff': return SupplierStaff.query.get(uid)
        # البحث الشامل في حال عدم تحديد النوع
        return AdminUser.query.get(uid) or Supplier.query.get(uid) or SupplierStaff.query.get(uid)
    except:
        return None

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # إضافة الفلاتر
    app.jinja_env.filters['full_time'] = format_full_timestamp

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app) # تفعيل الحماية عالمياً
    
    login_manager.login_view = 'suppliers_auth.login'

    # إتاحة csrf_token تلقائياً في كل القوالب
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # إنشاء قاعدة البيانات وتسجيل الموديولات
    with app.app_context():
        db.create_all()

        # زرع المستخدم الافتراضي
        try:
            admin = AdminUser.query.filter_by(username='علي محجوب').first()
            if not admin:
                admin = AdminUser(username='علي محجوب')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ خطأ أثناء زرع البيانات: {e}")

        # [التسجيل التلقائي للموديولات]
        apps_dir = os.path.join(app.root_path)
        # استثناء المجلدات غير البرمجية
        ignored_dirs = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'suppliers_auth']
        
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            # التأكد أنه مجلد وليس من المستثنيات
            if os.path.isdir(item_path) and item not in ignored_dirs:
                registry_file = os.path.join(item_path, 'registry.py')
                
                # إذا وجد ملف registry.py، نقوم بتسجيل الموديول تلقائياً
                if os.path.exists(registry_file):
                    try:
                        module_path = f"apps.{item}.registry"
                        module = importlib.import_module(module_path)
                        if hasattr(module, 'register_module'):
                            module.register_module(app)
                            print(f"✅ [Auto-Discovery] تم تسجيل موديول: {item}")
                    except Exception as e:
                        print(f"⚠️ [Auto-Discovery] فشل تسجيل {item}: {e}")

    return app
