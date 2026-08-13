# coding: utf-8
# 📂 apps/supplier_wallet/utils.py

from flask import session
from flask_login import current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet

# محاولة استيراد النماذج (Models) مع التعامل مع احتمالية عدم وجودها
try:
    from apps.models.supplier_db import Supplier, SupplierProfile
except ImportError:
    Supplier = None
    SupplierProfile = None

def get_current_supplier_id():
    """استخراج رقم المورد الحالي سواء كان تاجراً أو موظفاً"""
    if not current_user.is_authenticated:
        return None
    user_type = session.get('user_type')
    
    # إذا كان المستخدم موظفاً (Staff) نأخذ رقم المورد التابع له، وإلا نأخذ الـ ID مباشرة
    if user_type == 'staff':
        return getattr(current_user, 'supplier_id', None)
    
    return getattr(current_user, 'supplier_id', getattr(current_user, 'id', None))

def get_or_create_supplier_wallet(supplier_id):
    """جلب محفظة المورد أو إنشائها تلقائياً إذا لم تكن موجودة"""
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
                balance_sar=0.00,
                balance_pending=0.00,
                total_withdrawn=0.00
            )
            db.session.add(wallet)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # في حال فشل الإنشاء، نحاول البحث عنها مرة أخرى لضمان الاستمرارية
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
            
    return wallet

def get_registered_supplier_payout_info(supplier_id):
    """جلب بيانات السحب (اسم المالك وتفاصيل البنك) من السجلات الأساسية"""
    owner_name = ""
    account_details = ""
    
    # 1. البحث في نموذج المورد (Supplier)
    if Supplier and supplier_id:
        supplier_obj = Supplier.query.get(supplier_id)
        if supplier_obj:
            owner_name = getattr(supplier_obj, 'owner_name', None) or getattr(supplier_obj, 'trade_name', None) or ''

    # 2. البحث في نموذج البروفايل (SupplierProfile) إذا لم نجد بيانات
    if SupplierProfile and supplier_id:
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first()
        if profile:
            if not owner_name:
                owner_name = getattr(profile, 'owner_name', None) or getattr(profile, 'name', None) or ''
            if not account_details:
                account_details = getattr(profile, 'bank_details', None) or getattr(profile, 'account_details', None) or ''

    # 3. الاعتماد على المستخدم الحالي كخيار أخير
    if current_user.is_authenticated:
        if not owner_name:
            owner_name = getattr(current_user, 'owner_name', None) or getattr(current_user, 'full_name', '')
        if not account_details:
            account_details = getattr(current_user, 'bank_details', None) or getattr(current_user, 'account_details', '')

    return owner_name.strip(), account_details.strip()
