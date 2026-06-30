# coding: utf-8
# 📂 apps/__init__.py (النسخة المحدثة لنظام القيد المزدوج)

import os
import importlib
from decimal import Decimal
from flask import Flask, session
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_profile_db import SupplierProfile
from apps.utils.time_utils import format_full_timestamp

# ... [دالة load_user تبقى كما هي] ...

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
        
        try:
            # 1. إنشاء المستخدمين الأساسيين (كما هم)
            # ... [نفس كود إنشاء علي ووائل] ...
            
            # 2. زرع الطلب والمالية بنظام القيد المزدوج
            from apps.models.orders_db import Order
            from apps.models.financials_db import OrderFinancial
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            
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
                    amount_to_add = Decimal('1188.25')
                    
                    # القيد المحاسبي: إيداع للمورد (دائن في محفظته)
                    transaction = WalletTransaction(
                        wallet_id=wallet.id, 
                        owner_type='supplier',
                        owner_id=supplier.id,
                        credit=amount_to_add,  # <--- هذا هو التعديل: أصبح دائن
                        debit=0.00,
                        trans_type='credit', 
                        source_type='order', 
                        currency='SAR', 
                        description='مستحقات المورد عن طلب MAH-WEL9631', 
                        reference_number=custom_id,
                        related_order_id=custom_id
                    )
                    db.session.add(transaction)
                    
                    # ربط القيد بالمركز المالي للطلب
                    financial.transaction_id = transaction.id
                
                db.session.commit()
                print(f"✅ [Financial Engine]: تم تسجيل القيد المزدوج لـ {custom_id} بنجاح.")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Error]: {e}")

        # ... [كود الاكتشاف التلقائي كما هو] ...

    return app
