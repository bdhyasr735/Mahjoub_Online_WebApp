# coding: utf-8
# 📂 apps/supplier_wallet/utils.py

from flask import session, g
from flask_login import current_user
from apps.models.wallet_db import WalletTransaction


def get_current_supplier_id():
    """الحصول على معرّف المورد الحالي بمرونة وأمان من Flask-Login، السياق g، أو الجلسة"""
    # 1. التحقق من سياق الطلب g
    if hasattr(g, 'supplier_id') and g.supplier_id:
        return g.supplier_id

    # 2. التحقق من مستخدم Flask-Login الحالي
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

    # 3. التحقق من الجلسة المباشرة
    return session.get('supplier_id')


def get_trx_type_attr():
    """الحصول على حقل نوع المعاملة من نموذج المعاملات بشكل مرن"""
    for attr in ['trans_type', 'trx_type', 'transaction_type']:
        if hasattr(WalletTransaction, attr):
            return getattr(WalletTransaction, attr)
    return None
