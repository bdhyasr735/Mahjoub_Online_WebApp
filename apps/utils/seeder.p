# -*- coding: utf-8 -*-
from datetime import datetime
import secrets
import string
from sqlalchemy import select
from apps.extensions import db

def seed_database():
    """زراعة البيانات المبدئية بشكل آمن وديناميكي"""
    try:
        from apps.models.admin_db import AdminUser
        from apps.models.admin_staff_db import AdminStaff
        from apps.models.supplier_db import Supplier
        from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
        from apps.models.treasury_db import TreasuryEntry
    except ImportError as ie:
        print(f"⚠️ [تحذير استيراد الزراعة]: تعذر استيراد بعض النماذج: {ie}")
        return

    # 1. زراعة حساب المالك
    try:
        if not AdminUser.query.filter_by(username='ali_mahjoub').first():
            admin = AdminUser(username='ali_mahjoub', role='Owner')
            admin.set_password('123')
            db.session.add(admin)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع حساب المالك (ali_mahjoub) بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المالك]: {e}")

    # 2. زراعة موظف الإدارة
    try:
        if not AdminStaff.query.filter_by(username='admin_staff_test').first():
            staff = AdminStaff(
                username='admin_staff_test',
                name='موظف الإدارة التجريبي',
                email='admin_staff@mahjoub.online',
                role_title='مشرف عام الإدارة',
                is_active=True,
                permissions={
                    'manage_staff': True, 'manage_suppliers': True,
                    'manage_products': True, 'manage_orders': True, 'view_reports': True
                }
            )
            staff.set_password('123')
            db.session.add(staff)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع موظف الإدارة التجريبي بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة موظف الإدارة]: {e}")

    # 3. زراعة المورد التجريبي مع رقم الهاتف والمحفظة
    try:
        supplier = Supplier.query.filter_by(username='test_supplier').first()
        if not supplier:
            supplier = Supplier(
                username='test_supplier',
                trade_name='متجر محجوب التجريبي',
                owner_name='المورد التجريبي',
                store_name='متجر محجوب أونلاين',
                status='active',
                phone='779077746'  # رقم الهاتف المطلوب
            )
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()
        else:
            if not supplier.phone:
                supplier.phone = '779077746'
                db.session.commit()

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
            wallet_id=wallet.id, trans_type='deposit', amount=1000000.00
        ).first()

        if not existing_tx:
            now = datetime.utcnow()
            date_str = now.strftime('%Y%m%d')
            time_stamp = now.strftime('%H%M%S%f')[:9]
            characters = string.ascii_uppercase + string.digits

            while True:
                random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
                candidate_ref = f"TRX-SUP9631-{date_str}-{time_stamp}-{random_6_code}"
                if not db.session.scalar(select(WalletTransaction.id).where(WalletTransaction.reference_number == candidate_ref)):
                    seed_ref_number = candidate_ref
                    break

            seed_voucher_number = generate_unique_voucher_number(db.session.connection(), length=6, prefix="VCH-")

            initial_transaction = WalletTransaction(
                wallet_id=wallet.id, trans_type='deposit', status='completed',
                amount=1000000.00, currency='SAR', reference_number=seed_ref_number,
                voucher_number=seed_voucher_number, description="رصيد افتتاحي للمورد التجريبي"
            )
            db.session.add(initial_transaction)

            from apps.models.treasury_db import TreasuryEntry
            treasury_entry = TreasuryEntry(
                reference_number=seed_ref_number, voucher_number=seed_voucher_number,
                entry_type='deposit', amount=1000000.00, currency='SAR',
                owner_type='supplier', owner_id=supplier.id, description="سند إيداع رصيد افتتاحي"
            )
            db.session.add(treasury_entry)
            db.session.commit()
            print("✅ [الزراعة]: تم زرع المورد والمحفظة ومعاملة الرصيد الافتتاحي بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المورد والمحفظة]: {e}")
