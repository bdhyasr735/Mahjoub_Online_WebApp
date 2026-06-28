# coding: utf-8
# 📂 apps/__init__.py (نسخة الزرع الآمنة)

import os
import uuid
import importlib
from flask import Flask, session
from apps.extensions import db, login_manager, migrate
from apps.models.admin_db import AdminUser
from apps.models import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.supplier_profile_db import SupplierProfile

# ... (دالة load_user تبقى كما هي) ...
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

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'suppliers_auth.login' 

    with app.app_context():
        db.create_all()
        
        try:
            # 1. إنشاء المستخدمين
            if not AdminUser.query.filter_by(username='علي محجوب').first():
                admin = AdminUser(username='علي محجوب', role='Owner')
                admin.set_password('123')
                db.session.add(admin)
            
            supplier = Supplier.query.filter_by(username='وائل محجوب').first()
            if not supplier:
                supplier = Supplier(username='وائل محجوب', trade_name='محجوب أونلاين', phone='0500000000')
                supplier.set_password('123')
                db.session.add(supplier)
                db.session.flush() 
                profile = SupplierProfile(supplier_id=supplier.id, trade_name='محجوب أونلاين')
                db.session.add(profile)

            # 2. زرع الطلب التجريبي (مع توليد ID فريد يدوياً)
            from apps.models.orders_db import Order
            from apps.models.financials_db import OrderFinancial
            
            if not Order.query.filter_by(order_id_display='MJ-2026-001').first():
                # توليد ID فريد للنظام النصي
                unique_id = str(uuid.uuid4()) 
                
                real_order = Order(
                    id=unique_id, 
                    order_id_display='MJ-2026-001',
                    customer_name='عميل حقيقي - تجربة',
                    status='completed',
                    supplier_id=supplier.id,
                    total_price=1250.50
                )
                db.session.add(real_order)
                
                financial = OrderFinancial(
                    order_id=unique_id, # الربط بنفس الـ ID
                    total_paid=1250.50,
                    commission=62.25,
                    status='paid'
                )
                db.session.add(financial)
                print("✅ [Test Data]: تم زرع الطلب والبيانات المالية بنجاح.")

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Error]: {e}")

        # 3. الاكتشاف التلقائي (Auto-Discovery)
        # ... (كود الـ Auto-Discovery كما هو) ...
        apps_dir = app.root_path
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if item in ['__pycache__', 'models', 'extensions', 'static', 'templates', 'migrations']: continue
            registry_file = os.path.join(item_path, 'registry.py')
            if os.path.isdir(item_path) and os.path.exists(registry_file):
                try:
                    module = importlib.import_module(f"apps.{item}.registry")
                    if hasattr(module, 'register_module'): module.register_module(app)
                except Exception as e: print(f"⚠️ [Auto-Discovery] فشل تسجيل {item}: {e}")

    return app
