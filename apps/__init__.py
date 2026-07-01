# coding: utf-8
# 📂 apps/__init__.py

import os
import importlib
import uuid
from decimal import Decimal
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
        # 1. إعادة بناء الجداول بالهيكل الجديد (سيتم تنفيذ هذا بعد حذف الجداول من القاعدة)
        db.create_all()

        # 2. سكريبت زرع البيانات (Data Seed)
        try:
            # التأكد من وجود المورد الأساسي
            supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if not supplier:
                if not AdminUser.query.filter_by(username='علي محجوب').first():
                    admin = AdminUser(username='علي محجوب')
                    admin.set_password('123')
                    db.session.add(admin)
                
                supplier = Supplier(username='وائل محجوب', trade_name='محجوب أونلاين', phone='0500000000')
                supplier.set_password('123')
                db.session.add(supplier)
                db.session.flush()
                db.session.add(SupplierProfile(supplier_id=supplier.id, trade_name='محجوب أونلاين'))
                db.session.commit()

            # التأكد من وجود محفظة للمورد بالكود المعياري الجديد
            wallet_code = f"MAH-WEL{supplier.id}"
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
            if not wallet:
                wallet = SupplierWallet(wallet_code=wallet_code, supplier_id=supplier.id)
                db.session.add(wallet)
                db.session.commit()

            # زرع طلب تجريبي
            order_ref = "QAMRA-2026-001"
            if not Order.query.filter_by(order_reference=order_ref).first():
                new_order = Order(
                    id=str(uuid.uuid4()),
                    order_id_display="طلب-001",
                    supplier_id=supplier.id,
                    order_reference=order_ref,
                    total_price=500.00,
                    status='completed'
                )
                db.session.add(new_order)
                db.session.flush()

                financial = OrderFinancial(
                    order_id=new_order.id,
                    supplier_id=supplier.id,
                    currency='SAR',
                    supplier_cost=400.00,
                    mahjoub_commission=100.00,
                    total_paid=500.00,
                    settlement_status='settled'
                )
                db.session.add(financial)

                # إضافة الحركات المالية
                db.session.add(WalletTransaction(wallet_id=wallet.id, owner_id=supplier.id, trans_type='supplier_cost', amount=400.00, currency='SAR'))
                db.session.add(WalletTransaction(wallet_id=wallet.id, owner_id=1, trans_type='platform_commission', amount=100.00, currency='SAR'))
                
                db.session.commit()
                print("🚀 [الخزينة]: تم إعادة بناء الجداول وتسجيل الحركات المالية بنجاح!")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Data Seed Error]: {e}")

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
