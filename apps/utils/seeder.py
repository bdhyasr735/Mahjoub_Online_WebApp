# -*- coding: utf-8 -*-
# 📂 apps/utils/seeder.py

"""
وحدة الزراعة (Seeder)
تقوم بزراعة البيانات المبدئية في قاعدة البيانات بشكل آمن وديناميكي
"""

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
            supplier.phone = '967779077746'  # ✅ تم تصحيح الرقم ليطابق الصيغة الكاملة والمدعومة
            supplier.set_password('123')
            db.session.add(supplier)
            db.session.flush()
            print("✅ [الزراعة]: تم إنشاء المورد التجريبي.")
        else:
            print("ℹ️ [الزراعة]: المورد التجريبي موجود مسبقاً، يتم تحديث بياناته الأساسية...")
            supplier.phone = '967779077746'  # ✅ تصحيح الرقم هنا أيضاً لتجنب أي مشاكل بالبحث أو الواتساب
            supplier.set_password('123')
            db.session.commit()
            print("✅ [الزراعة]: تم تحديث بيانات المورد وكلمة المرور بنجاح.")

        # إنشاء المحفظة (تم التحديث لاستخدام balance و currency بدلاً من balance_sar و status)
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        if not wallet:
            wallet = SupplierWallet(
                supplier_id=supplier.id,
                wallet_code=f"WEL-963{supplier.id}",
                balance=1000000.00,
                currency="SAR",
                is_active=True
            )
            db.session.add(wallet)
            db.session.flush()
            print("✅ [الزراعة]: تم إنشاء محفظة المورد.")
        else:
            print("ℹ️ [الزراعة]: محفظة المورد موجودة مسبقاً.")

        # التحقق من وجود معاملة الرصيد الافتتاحي
        existing_tx = WalletTransaction.query.filter_by(
            wallet_id=wallet.id,
            transaction_type='deposit',
            amount=1000000.00
        ).first()

        if not existing_tx:
            # إنشاء رقم مرجعي فريد
            now = datetime.utcnow()
            date_str = now.strftime('%Y%m%d')
            time_stamp = now.strftime('%H%M%S%f')[:9]
            characters = string.ascii_uppercase + string.digits

            # توليد رقم مرجعي فريد
            while True:
                random_6_code = ''.join(secrets.choice(characters) for _ in range(6))
                candidate_ref = f"TRX-SUP9631-{date_str}-{time_stamp}-{random_6_code}"
                exists_ref = db.session.scalar(
                    select(WalletTransaction.id).where(
                        WalletTransaction.description == candidate_ref
                    )
                )
                if not exists_ref:
                    seed_ref_number = candidate_ref
                    break

            # توليد رقم سند فريد
            seed_voucher_number = generate_unique_voucher_number()

            # إنشاء معاملة الإيداع
            initial_transaction = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type='deposit',
                amount=1000000.00,
                description=f"رصيد افتتاحي للمورد التجريبي عند إعداد المحفظة - مرجع: {seed_ref_number} - سند: {seed_voucher_number}"
            )
            db.session.add(initial_transaction)
            print("✅ [الزراعة]: تم إنشاء معاملة الإيداع الافتتاحية.")

            # إنشاء سند الخزينة (إذا كان النموذج يدعمه)
            try:
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
                print("✅ [الزراعة]: تم إنشاء سند الخزينة.")
            except Exception as te:
                print(f"ℹ️ [تخطي سند الخزينة]: {te}")

            db.session.commit()
            print("=" * 60)
            print("✅ [الزراعة]: تم زرع المورد والمحفظة وخزينة الرصيد الافتتاحي بنجاح.")
            print(f"    📌 اسم المورد: {supplier.trade_name}")
            print(f"    📌 كود المورد: SUP-963{supplier.id}")
            print(f"    📌 كود المحفظة: WEL-963{supplier.id}")
            print(f"    📌 الرصيد: 1,000,000 SAR")
            print(f"    📌 رقم السند: {seed_voucher_number}")
            print(f"    📌 الرقم المرجعي: {seed_ref_number}")
            print("=" * 60)
        else:
            print("ℹ️ [الزراعة]: معاملة الرصيد الافتتاحي موجودة مسبقاً.")
            
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [خطأ زراعة المورد والمحفظة]: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# دالة مساعدة لتشغيل الزراعة من سكربت منفصل
# ============================================================
def run_seeder():
    """تشغيل عملية الزراعة مع سياق التطبيق"""
    try:
        from flask import current_app
        with current_app.app_context():
            seed_database()
    except RuntimeError:
        # إذا لم يكن هناك سياق تطبيق، قم بإنشاء تطبيق مؤقت
        from apps import create_app
        app = create_app()
        with app.app_context():
            seed_database()


if __name__ == "__main__":
    # تشغيل السكربت مباشرة
    print("🚀 بدء تشغيل سكربت الزراعة...")
    run_seeder()
    print("✅ انتهى تشغيل سكربت الزراعة.")
