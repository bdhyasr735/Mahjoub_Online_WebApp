# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
from flask import Flask, session
from apps.extensions import db, login_manager, migrate
from apps.models import AdminUser, Supplier, SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet
from apps.utils.time_utils import format_full_timestamp

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
    app.jinja_env.filters['full_time'] = format_full_timestamp

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'suppliers_auth.login'

    with app.app_context():
        # 1. إنشاء الجداول (سيعيد إنشاء أي جداول مفقودة بعد حذفنا اليدوي في Neon)
        db.create_all()

        # 2. سكريبت زرع البيانات (Data Seed) المحمي والمجزأ
        
        # --- الجزء الأول: إنشاء المسؤول ---
        try:
            admin = AdminUser.query.filter_by(username='علي محجوب').first()
            if not admin:
                admin = AdminUser(username='علي محجوب')
                admin.set_password('123')
                db.session.add(admin)
                db.session.commit()
                print("✅ [Seed]: تم إنشاء المسؤول بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Admin Seed Error]: {e}")

        # --- الجزء الثاني: إنشاء المورد والملف الشخصي ---
        try:
            supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if not supplier:
                supplier = Supplier(username='وائل محجوب', trade_name='محجوب أونلاين', phone='0500000000')
                supplier.set_password('123')
                db.session.add(supplier)
                db.session.commit() 
                
                db.session.add(SupplierProfile(supplier_id=supplier.id, trade_name='محجوب أونلاين'))
                db.session.commit()
                print("✅ [Seed]: تم إنشاء المورد وملفه الشخصي بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Supplier Seed Error]: {e}")

        # --- الجزء الثالث: إنشاء المحفظة (معزول لضمان استقرار الدخول) ---
        try:
            current_supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if current_supplier:
                wallet = SupplierWallet.query.filter_by(supplier_id=current_supplier.id).first()
                if not wallet:
                    db.session.add(SupplierWallet(wallet_code=f"MAH-WEL{current_supplier.id}", supplier_id=current_supplier.id))
                    db.session.commit()
                    print("✅ [Seed]: تم إنشاء المحفظة بنجاح.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Wallet Seed Error]: {e}")

        # 3. الاكتشاف التلقائي للموديولات
        apps_dir = app.root_path
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if item in ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations', 'utils', 'suppliers_auth']: continue
            registry_file = os.path.join(item_path, 'registry.py')
            if os.path.isdir(item_path) and os.path.exists(registry_file):
                try:
                    module = importlib.import_module(f"apps.{item}.registry")
                    if hasattr(module, 'register_module'): 
                        module.register_module(app)
                except Exception as e: 
                    print(f"⚠️ [Auto-Discovery] فشل تسجيل {item}: {e}")

    return app
