# -*- coding: utf-8 -*-
# 📂 apps/__init__.py

import os
import importlib
import secrets
import string
import click
from datetime import datetime
from flask import Flask, redirect, session, url_for, request, jsonify, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_talisman import Talisman
from flask_cors import CORS
from sqlalchemy import text, select
import config
from apps.extensions import db, login_manager, migrate, limiter
from apps.services.graphql_client import GraphQLClient

ADMIN_MODULES = {}
SUPPLIER_MODULES = {}


def import_all_models():
    """استيراد جميع ملفات النماذج تلقائياً من مجلد apps/models لضمان التعرف على جميع الجداول والأنواع."""
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.py') and not file.startswith('__'):
                module_name = file[:-3]
                try:
                    importlib.import_module(f"apps.models.{module_name}")
                except Exception as e:
                    print(f"⚠️ [خطأ في استيراد النموذج] فشل استيراد النموذج '{module_name}': {e}")


def seed_database():
    """
    زراعة البيانات المبدئية بشكل آمن وديناميكي.
    يتم التحقق من وجود البيانات قبل إضافتها لتجنب التكرار.
    """
    try:
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
        from apps.models.treasury_db import TreasuryEntry
    except ImportError as ie:
        print(f"⚠️ [تحذير استيراد الزراعة]: تعذر استيراد بعض النماذج: {ie}")
        return

    # ============================================================
    # 1. زراعة حساب المالك (Owner)
    # ============================================================
    try:
        if not AdminUser.query.filter_by(username='ali_mahjoub').first():
            admin = AdminUser(username='ali_mahjoub', role='Owner')
            admin.set_password('123')
            db.session.add(admin)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع حساب المالك (ali_mahjoub) بنجاح.")
        else:
            print("ℹ️ [الزراعة]: حساب المالك موجود مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المالك]: {e}")

    # ============================================================
    # 2. زراعة موظف إدارة (Admin Staff)
    # ============================================================
    try:
        if not AdminStaff.query.filter_by(username='admin_staff_test').first():
            staff = AdminStaff(
                username='admin_staff_test',
                name='موظف الإدارة التجريبي',
                email='admin_staff@mahjoub.online',
                role_title='مشرف عام الإدارة',
                is_active=True,
                permissions={
                    'manage_staff': True,
                    'manage_suppliers': True,
                    'manage_products': True,
                    'manage_orders': True,
                    'view_reports': True
                }
            )
            staff.set_password('123')
            db.session.add(staff)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع موظف الإدارة التجريبي (admin_staff_test) بنجاح.")
        else:
            print("ℹ️ [الزراعة]: موظف الإدارة موجود مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة موظف الإدارة]: {e}")

    # ============================================================
    # 3. زراعة مورد تجريبي مع محفظة ورصيد افتتاحي
    # ============================================================
    try:
        supplier = Supplier.query.filter_by(username='test_supplier').first()
        if not supplier:
            supplier = Supplier(
                username='test_supplier',
                trade_name='متجر محجوب التجريبي',
                owner_name='المورد التجريبي',
                store_name='متجر محجوب أونلاين',
                status='active'
            )
            supplier.phone = '779077746'
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()

        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        if not wallet:
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"MAH-WEL963{supplier.id}",
                balance_sar=1000000.00,
                status='active'
            )
            db.session.add(wallet)
            db.session.flush()

        existing_tx = WalletTransaction.query.filter_by(
            wallet_id=wallet.id,
            trans_type='deposit',
            amount=1000000.00
        ).first()

        if not existing_tx:
            now = datetime.utcnow()
            date_str = now.strftime('%Y%m%d')
            time_stamp = now.strftime('%H%M%S%f')[:9]
            characters = string.ascii_uppercase + string.digits

            while True:
                random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
                candidate_ref = f"TRX-SUP9631-{date_str}-{time_stamp}-{random_6_code}"
                exists_ref = db.session.scalar(
                    select(WalletTransaction.id).where(
                        WalletTransaction.reference_number == candidate_ref
                    )
                )
                if not exists_ref:
                    seed_ref_number = candidate_ref
                    break

            seed_voucher_number = generate_unique_voucher_number(
                db.session.connection(),
                length=6,
                prefix="VCH-"
            )

            initial_transaction = WalletTransaction(
                wallet_id=wallet.id,
                trans_type='deposit',
                status='completed',
                amount=1000000.00,
                currency='SAR',
                reference_number=seed_ref_number,
                voucher_number=seed_voucher_number,
                description="رصيد افتتاحي للمورد التجريبي عند إعداد المحفظة"
            )
            db.session.add(initial_transaction)

            treasury_entry = TreasuryEntry(
                reference_number=seed_ref_number,
                voucher_number=seed_voucher_number,
                entry_type='deposit',
                amount=1000000.00,
                currency='SAR',
                owner_type='supplier',
                owner_id=supplier.id,
                description="سند إيداع رصيد افتتاحي للمورد التجريبي (الخزينة العامة)"
            )
            db.session.add(treasury_entry)

            db.session.commit()
            print("✅ [الزراعة]: تم زرع المورد والمحفظة وخزينة الرصيد الافتتاحي (1,000,000 SAR) بنجاح.")
            print(f"    📌 كود المورد: SUP-963{supplier.id}")
            print(f"    📌 كود المحفظة: WEL-963{supplier.id}")
            print(f"    📌 رقم السند: {seed_voucher_number}")
        else:
            print("ℹ️ [الزراعة]: المورد التجريبي والمحفظة ومعاملة الرصيد الافتتاحي موجودة مسبقاً.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المورد والمحفظة]: {e}")


def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config.from_object('config.Config')
    config.Config.validate_config()

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_ENV') == 'production',
        SESSION_COOKIE_SAMESITE='Lax',
    )

    # ============================================================
    # 🔌 إعدادات الاتصال بقاعدة البيانات
    # ============================================================
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    db.init_app(app)
    app.jinja_env.globals.update(getattr=getattr)

    CORS(app, resources={
        r"/admin/graphql*": {
            "origins": [
                "https://studio.apollographql.com",
                "https://embed.apollographql.com",
                "https://sandbox.embed.apollographql.com",
                "http://localhost:5000",
                "https://mahjoub.online"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Apollo-Require-Preflight",
                "Accept"
            ],
            "supports_credentials": True
        }
    })

    # ============================================================
    # ⚙️ تنظيف وتفريغ الجلسات عند انتهاء الطلب أو وقوع خطأ
    # ============================================================
    @app.teardown_request
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.remove()

    @app.errorhandler(500)
    def handle_500_error(e):
        db.session.rollback()
        # تم تعديل رسالة الخطأ هنا لتظهر بشكل نصي صحيح بدلاً من رموز اليونيكود
        return jsonify({"error": "Internal Server Error", "message": "حدث خطأ داخلي في الخادم"}), 500

    # ============================================================
    # ⚙️ التهيئة وإعادة بناء الجداول بالكامل عند عملية الرفع
    # ============================================================
    with app.app_context():
        import_all_models()
        try:
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()
            print("✅ [إعادة البناء الكامل]: تم حذف جميع الجداول القديمة وإعادة تعيين الـ Schema بنجاح.")

            db.create_all()
            print("✅ [إنشاء الجداول]: تم إنشاء جميع الجداول بنجاح.")

            seed_database()
            print("✅ [الزراعة التلقائية]: تمت زراعة البيانات المبدئية بنجاح.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ [خطأ في إعادة بناء الجداول]: {e}")

    # ============================================================
    # ⚙️ أمر CLI لإعادة بناء القاعدة يدوياً
    # ============================================================
    @app.cli.command("rebuild-db")
    def rebuild_db_command():
        """ح
