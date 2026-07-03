# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
import traceback
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from apps.extensions import db, login_manager, migrate
from apps.models import AdminUser, Supplier, SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.utils.time_utils import format_full_timestamp

# تهيئة الحماية العالمية
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'admin': return AdminUser.query.get(int(user_id))
    elif user_type == 'supplier': return Supplier.query.get(int(user_id))
    elif user_type == 'staff': return SupplierStaff.query.get(int(user_id))
    return AdminUser.query.get(int(user_id)) or Supplier.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # إضافة الفلتر المخصص
    app.jinja_env.filters['full_time'] = format_full_timestamp

    # تهيئة الإضافات الأساسية
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'suppliers_auth.login'

    # 🛡️ الحماية الأمنية العالمية (Security Headers)
    @app.after_request
    def add_security_headers(response):
        # منع أرشفة جوجل (SEO Protection): يمنع محركات البحث من أرشفة لوحات التحكم
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
        # الحماية من حقن النصوص (XSS)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # الحماية من النقر المتقاطع (Clickjacking)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    # إتاحة csrf_token في جميع قوالب Jinja2
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    with app.app_context():
        # إنشاء الجداول (تأكد أن كل الموديلات تم استيرادها في الأعلى)
        db.create_all()

        # زرع بيانات المسؤول الأول
        try:
            admin = AdminUser.query.filter_by(username='علي محجوب').first()
            if not admin:
                admin = AdminUser(username='علي محجوب')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
        except Exception:
            db.session.rollback()

        # 🔍 نظام الاكتشاف التلقائي للموديولات (مع كشف الأخطاء الذكي)
        apps_dir = app.root_path
        # المجلدات التي لا يجب أن يعاملها النظام كموديولات
        excluded = ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'suppliers_auth']
        
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            # تخطي المجلدات المستثناة أو الملفات العادية
            if item in excluded or not os.path.isdir(item_path):
                continue
            
            # البحث عن ملف التسجيل
            registry_file = os.path.join(item_path, 'registry.py')
            if os.path.exists(registry_file):
                try:
                    # استيراد الموديول ديناميكياً
                    module = importlib.import_module(f"apps.{item}.registry")
                    if hasattr(module, 'register_module'): 
                        module.register_module(app)
                except Exception:
                    # إذا انهار موديول معين، سيطبع لنا الخطأ كاملاً دون إيقاف باقي النظام (إن أمكن)
                    print(f"\n❌ [CRITICAL ERROR] فشل تحميل الموديول: {item}")
                    traceback.print_exc() 

    return app
