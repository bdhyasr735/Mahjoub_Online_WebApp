# coding: utf-8
# 📂 apps/supplier_wallet/utils.py

from datetime import datetime
from typing import Optional, Tuple
from decimal import Decimal
from flask import session
from flask_login import current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# محاولة استيراد النماذج (Models) مع التعامل مع احتمالية عدم وجودها
try:
    from apps.models.supplier_db import Supplier, SupplierProfile
except ImportError:
    Supplier = None
    SupplierProfile = None


def get_current_supplier_id() -> Optional[int]:
    """استخراج رقم المورد الحالي سواء كان تاجراً أو موظفاً."""
    if not current_user or not getattr(current_user, 'is_authenticated', False):
        return None

    user_type = session.get('user_type')

    # إذا كان المستخدم موظفاً (Staff) نأخذ رقم المورد التابع له
    if user_type == 'staff':
        return getattr(current_user, 'supplier_id', None)

    # المورد المباشر أو المعرف الأساسي للمستخدم
    return getattr(current_user, 'supplier_id', getattr(current_user, 'id', None))


def generate_transaction_ref(wallet_id: int, sup_code: str, prefix: str = 'TRX') -> Tuple[Optional[str], Optional[str]]:
    """
    دالة موحدة لتوليد الرقم المرجعي ورقم السند عند الحاجة فقط للعمليات المالية النظامية المباشرة.
    تُعيد (None, None) عند الاستدعاء الخاطئ لتجنب إسناد أرقام مرجعية تلقائية غير مطابقة.
    """
    if not wallet_id or not sup_code:
        return None, None

    now = datetime.utcnow()
    date_str = now.strftime('%Y%m%d')
    start_of_day = datetime(now.year, now.month, now.day)

    # حساب تسلسل اليوم للحركات التابعة لهذه المحفظة
    daily_count = db.session.query(WalletTransaction)\
        .filter(
            WalletTransaction.wallet_id == wallet_id,
            WalletTransaction.created_at >= start_of_day
        ).count() + 1

    # حلقة حماية لضمان عدم وجود تكرار نهائياً في قاعدة البيانات
    while True:
        seq_str = f"{daily_count:04d}"
        ref_number = f"{prefix}-{sup_code}-{date_str}-{seq_str}"
        
        exists = db.session.query(WalletTransaction.id)\
            .filter(WalletTransaction.reference_number == ref_number)\
            .first()
        
        if not exists:
            break
        daily_count += 1

    vch_number = f"VCH-{sup_code}-{date_str}-{seq_str}"
    return ref_number, vch_number


def get_or_create_supplier_wallet(supplier_id: Optional[int]) -> Optional[SupplierWallet]:
    """جلب محفظة المورد أو إنشائها تلقائياً إذا لم تكن موجودة بأمان مع معالجة سباق البيانات (Race Conditions)."""
    if not supplier_id:
        return None

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()

    if not wallet:
        try:
            # محاولة الحصول على كود المورد لإنشاء كود محفظة فريد
            sup_code = None
            if Supplier:
                supplier_obj = Supplier.query.get(supplier_id)
                if supplier_obj:
                    sup_code = getattr(supplier_obj, 'supplier_code', None)

            if not sup_code:
                sup_code = f"SUP{supplier_id}"

            wallet = SupplierWallet(
                supplier_id=supplier_id,
                wallet_code=f"WEL-{sup_code}",
                balance_sar=Decimal('0.00'),
                balance_pending=Decimal('0.00'),
                total_withdrawn=Decimal('0.00')
            )
            db.session.add(wallet)
            db.session.commit()
        except Exception:
            db.session.rollback()
            # في حال فشل الإنشاء التزمني، نحاول البحث مرة أخرى لضمان الاستمرارية
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()

    return wallet


def get_registered_supplier_payout_info(supplier_id: Optional[int]) -> Tuple[str, str]:
    """جلب بيانات السحب (اسم المالك وتفاصيل البنك/الحساب) من السجلات الأساسية المتاحة."""
    owner_name = ""
    account_details = ""

    # 1. البحث في نموذج المورد (Supplier)
    if Supplier and supplier_id:
        supplier_obj = Supplier.query.get(supplier_id)
        if supplier_obj:
            owner_name = getattr(supplier_obj, 'owner_name', None) or getattr(supplier_obj, 'trade_name', None) or ''

    # 2. البحث في نموذج البروفايل (SupplierProfile) إذا لم نجد البيانات
    if SupplierProfile and supplier_id:
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
        if profile:
            if not owner_name:
                owner_name = getattr(profile, 'owner_name', None) or getattr(profile, 'name', None) or ''
            if not account_details:
                account_details = getattr(profile, 'bank_details', None) or getattr(profile, 'account_details', None) or ''

    # 3. الاعتماد على المستخدم الحالي كخيار أخير في حالة نقص البيانات
    if current_user and getattr(current_user, 'is_authenticated', False):
        if not owner_name:
            owner_name = getattr(current_user, 'owner_name', None) or getattr(current_user, 'full_name', '') or ''
        if not account_details:
            account_details = getattr(current_user, 'bank_details', None) or getattr(current_user, 'account_details', '') or ''

    return owner_name.strip(), account_details.strip()
