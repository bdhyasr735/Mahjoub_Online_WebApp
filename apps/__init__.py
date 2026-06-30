# coding: utf-8
# 📂 apps/__init__.py

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
        
        # 1. تهيئة النظام (بيانات أساسية)
        try:
            # [هنا تضع منطق إنشاء الأدمن والمورد كما في كودك]
            
            # 2. رحلة الطلب وسند التسوية (توليد حركة مالية)
            from apps.models.orders_db import Order
            from apps.models.financials_db import OrderFinancial
            from apps.models.wallet_db import SupplierWallet, WalletTransaction
            
            custom_id = 'MAH-WEL9631'
            if not Order.query.filter_by(id=custom_id).first():
                # أ. تسجيل الطلب
                order = Order(id=custom_id, order_id_display='MJ-2026-001', 
                              status='completed', total_price=1250.50)
                db.session.add(order)
                
                # ب. إنشاء سند التسوية (الجانب المحاسبي)
                fin = OrderFinancial(order_id=custom_id, total_paid=1250.50, 
                                     mahjoub_commission=62.25, supplier_cost=1188.25)
                db.session.add(fin)
                
                # ج. حركة المحفظة (الترحيل للخزينة)
                wallet = SupplierWallet.query.first()
                if wallet:
                    trans = WalletTransaction(
                        wallet_id=wallet.id, trans_type='credit',
                        amount=Decimal('1188.25'), description='تسوية طلب MJ-2026-001',
                        reference_number=custom_id
                    )
                    db.session.add(trans)
                    wallet.balance_sar += Decimal('1188.25')
                
                db.session.commit()
                print("✅ [الرحلة المالية]: اكتملت بنجاح لطلب MAH-WEL9631")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Error]: {e}")

    return app
