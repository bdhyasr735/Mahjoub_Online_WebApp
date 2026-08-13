# coding: utf-8
# 📂 apps/supplier_wallet/utils.py

from flask import session
from flask_login import current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction

try:
    from apps.models.supplier_db import Supplier, SupplierProfile
except ImportError:
    Supplier = None
    SupplierProfile = None

def get_trx_type_attr():
    """التحقق الديناميكي من اسم حقل نوع المعاملة لتجنب الخصائص البرمجية"""
    for col_name in ['transaction_type', 'trx_type', 'trans_type']:
        if hasattr(WalletTransaction, col_name):
            attr = getattr(WalletTransaction, col_name)
            if not isinstance(attr, property):
                return attr
    return None

def get_status_attr():
    """التحقق الديناميكي من اسم حقل الحالة"""
    for col_name in ['status', 'state']:
        if hasattr(WalletTransaction, col_name):
            attr = getattr(WalletTransaction, col_name)
            if not isinstance(attr, property):
                return attr
    return None

def get_current_supplier_id():
    """استخراج رقم المورد الحالي سواء كان تاجراً أو موظفاً"""
    if not current_user.is_authenticated:
        return None
    user_type = session.get('user_type')
    if user_type == 'supplier':
        return getattr(current_user, 'id', None)
    elif user_type == 'staff':
        return getattr(current_user, 'supplier_id', None)
    return getattr(current_user, 'supplier_id', getattr(current_user, 'id', None))

def get_or_create_supplier_wallet(supplier_id):
    """جلب محفظة المورد أو إنشائها تلقائياً"""
    if not supplier_id:
        return None
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        try:
            sup_code = None
            if Supplier:
                supplier_obj = Supplier.query.get(supplier_id)
                if supplier_obj:
                    sup_code = getattr(supplier_obj, 'supplier_code', None)
            
            if not sup_code:
                sup_code = f"MAH-SUP963{supplier_id}"

            wallet = SupplierWallet(
                supplier_id=supplier_id,
                wallet_code=f"WEL-{sup_code}",
                balance_sar=0.00
            )
            db.session.add(wallet)
            db.session.commit()
        except Exception:
            db.session.rollback()
            wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    return wallet

def get_registered_supplier_payout_info(supplier_id):
    """جلب بيانات السحب الخاصة بالمورد من السجلات الأساسية"""
    owner_name = ""
    account_details = ""
    
    if Supplier and supplier_id:
        supplier_obj = Supplier.query.get(supplier_id)
        if supplier_obj:
            owner_name = getattr(supplier_obj, 'owner_name', None) or getattr(supplier_obj, 'trade_name', None) or ''

    if SupplierProfile and supplier_id and not account_details:
        profile = SupplierProfile.query.filter_by(supplier_id=supplier_id).first() or SupplierProfile.query.filter_by(id=supplier_id).first()
        if profile:
            if not owner_name:
                owner_name = getattr(profile, 'owner_name', None) or getattr(profile, 'name', None) or getattr(profile, 'full_name', '')
            account_details = getattr(profile, 'bank_details', None) or getattr(profile, 'account_details', None) or getattr(profile, 'payout_info', '')

    if not owner_name and current_user.is_authenticated:
        owner_name = getattr(current_user, 'owner_name', None) or getattr(current_user, 'full_name', None) or getattr(current_user, 'name', '') or getattr(current_user, 'username', '')

    if not account_details and current_user.is_authenticated:
        account_details = getattr(current_user, 'bank_details', None) or getattr(current_user, 'account_details', '')

    return owner_name.strip(), account_details.strip()
