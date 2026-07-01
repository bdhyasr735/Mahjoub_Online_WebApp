# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
import uuid
from flask import Flask, session
from apps.extensions import db, login_manager, migrate
from apps.models import AdminUser, Supplier, SupplierProfile
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.financials_db import OrderFinancial
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.orders_db import Order 
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
        # 1. التحديث التلقائي للهيكل (خارج نطاق إدارة الموديلات المباشرة لتجنب تضارب الذاكرة)
        try:
            with db.engine.connect() as conn:
                # إضافة الأعمدة المطلوبة إذا لم تكن موجودة
                cols = {
                    'wallet_code': 'VARCHAR(50)', 'supplier_id': 'INTEGER', 
                    'balance_yer': 'NUMERIC(18,2)', 'balance_usd': 'NUMERIC(18,2)', 
                    'balance_sar': 'NUMERIC(18,2)', 'balance_pending': 'NUMERIC(18,2)'
                }
                for col_name, col_type in cols.items():
                    try:
                        conn.execute(db.text(f"ALTER TABLE supplier_wallets ADD COLUMN {col_name} {col_type} DEFAULT 0.00"))
                        conn.commit()
                    except: 
                        pass # هذا يعني أن العمود موجود بالفعل
        except: 
            pass

        # 2. إنشاء أي جداول جديدة
        db.create_all()

        # 3. سكريبت زرع البيانات (Data Seed) - تم إضافة تحقق إضافي
        try:
            supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if not supplier:
                # إنشاء المورد
                supplier = Supplier(username='وائل محجوب', trade_name='محجوب أونلاين', phone='0500000000')
                supplier.set_password('123')
                db.session.add(supplier)
                db.session.flush()
                db.session.add(SupplierProfile(supplier_id=supplier.id, trade_name='محجوب أونلاين'))
                db.session.commit()

            # إنشاء المحفظة
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            if not wallet:
                wallet = SupplierWallet(wallet_code=f"MAH-WEL{supplier.id}", supplier_id=supplier.id)
                db.session.add(wallet)
                db.session.commit()

            print("🚀 [System]: تم التأكد من سلامة هيكل قاعدة البيانات والبيانات الأساسية.")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Data Seed Error]: {e}")

        # 4. الاكتشاف التلقائي للموديولات
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
