# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/utils.py

from flask import session, g
from flask_login import current_user
from apps.models.wallet_db import WalletTransaction, SupplierWallet
import re

def get_current_supplier_id():
    """الحصول على معرّف المورد الحالي بمرونة وأمان من Flask-Login، السياق g، أو الجلسة"""
    if hasattr(g, 'supplier_id') and g.supplier_id:
        return g.supplier_id

    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        user_type = session.get('user_type')
        if user_type == 'staff':
            return getattr(current_user, 'supplier_id', None)
        elif user_type == 'supplier':
            return getattr(current_user, 'id', None)
        elif hasattr(current_user, 'supplier_id'):
            return current_user.supplier_id
        elif hasattr(current_user, 'id'):
            return current_user.id

    return session.get('supplier_id')


def get_current_wallet_identifier():
    """الحصول على رقم المحفظة أو معرف المورد بصيغة آمنة للرابط (بدون استخدام general)"""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
        
    if not supplier_id:
        return '1'  # معرف افتراضي آمن يمنع ظهور كلمة general تماماً
    
    # البحث عن محفظة المورد لجلب رقمها أو معرفها الفريد
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if wallet:
        if hasattr(wallet, 'wallet_code') and wallet.wallet_code:
            return str(wallet.wallet_code)
        if hasattr(wallet, 'account_number') and wallet.account_number:
            return str(wallet.account_number)
        return str(wallet.id)
        
    trade_name = getattr(current_user, 'trade_name', None)
    if trade_name:
        slug = re.sub(r'[^\w\s-]', '', trade_name).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        if slug:
            return slug
            
    return str(supplier_id)


def get_trx_type_attr():
    """الحصول على حقل نوع المعاملة من نموذج المعاملات بشكل مرن"""
    for attr in ['trans_type', 'trx_type', 'transaction_type']:
        if hasattr(WalletTransaction, attr):
            return getattr(WalletTransaction, attr)
    return None
