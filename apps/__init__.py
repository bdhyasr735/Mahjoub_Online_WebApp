# coding: utf-8
import os
import importlib
from decimal import Decimal
from flask import Flask, session
from werkzeug.security import generate_password_hash
from apps.extensions import db, login_manager, migrate
from apps.models import AdminUser, Supplier, SupplierProfile, SupplierWallet, WalletTransaction, Order, OrderFinancial
from apps.models.supplier_staff_db import SupplierStaff
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
        db.create_all()
        
        # 1. زرع البيانات الأساسية والمالية
        try:
            # زرع المالك: علي محجوب
            admin = AdminUser.query.filter_by(username='Ali Mahjoub').first()
            if not admin:
                admin = AdminUser(username='Ali Mahjoub', password=generate_password_hash('123'))
                db.session.add(admin)
                db.session.commit()
                print("✅ [Seed]: تم زرع المالك علي محجوب بنجاح.")

            # زرع المورد وتفاصيل الطلب
            supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if not supplier:
                supplier = Supplier(username='وائل محجوب', trade_name='محجوب أونلاين', phone='0500000000')
                supplier.set_password('123')
                db.session.add(supplier)
                db.session.flush()
                db.session.add(SupplierProfile(supplier_id=supplier.id, trade_name='محجوب أونلاين'))
                db.session.commit()

            custom_id = 'MAH-WEL9631'
            if not Order.query.filter_by(id=custom_id).first():
                real_order = Order(id=custom_id, order_id_display='MJ-2026-001', 
                                   customer_name='عميل تجربة', status='completed', 
                                   supplier_id=supplier.id, total_price=1250.50)
                db.session.add(real_order)
                
                financial = OrderFinancial(order_id=custom_id, supplier_id=supplier.id, 
                                           total_paid=1250.50, mahjoub_commission=62.25, 
                                           supplier_cost=1188.25, settlement_status='paid')
                db.session.add(financial)
                
                wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
                if wallet:
                    amount = Decimal('1188.25')
                    # تم إصلاح الخطأ هنا: إزالة credit= و debit= واستخدام الحقول المتاحة فقط
                    transaction = WalletTransaction(
                        wallet_id=wallet.id, owner_type='supplier', owner_id=supplier.id,
                        amount=amount, trans_type='credit', 
                        source_type='order', currency='SAR', 
                        description='مستحقات المورد MAH-WEL9631', 
                        reference_number=custom_id, related_order_id=custom_id
                    )
                    db.session.add(transaction)
                    db.session.flush()
                    financial.transaction_id = transaction.id
                    wallet.balance_sar = (wallet.balance_sar or Decimal('0.00')) + amount
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Data Seed Error]: {e}")

        # 2. الاكتشاف التلقائي للموديولات
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
