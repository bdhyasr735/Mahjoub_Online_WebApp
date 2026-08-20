# coding: utf-8
"""
📂 apps/supplier_wallet/utils.py
الأدوات المساعدة لموديول المحفظة المالية
"""

from flask import session, g
from models.wallet_models import WalletTransaction

def get_current_supplier_id():
    """الحصول على معرّف المورد الحالي من الجلسة أو السياق"""
    if hasattr(g, 'supplier_id') and g.supplier_id:
        return g.supplier_id
    if hasattr(g, 'user') and hasattr(g.user, 'id'):
        return g.user.id
    return session.get('supplier_id', 1)

def get_trx_type_attr():
    """الحصول على حقل نوع المعاملة من نموذج المعاملات"""
    return getattr(WalletTransaction, 'trans_type', None)
