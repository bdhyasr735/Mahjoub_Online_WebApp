# coding: utf-8
# 📂 apps/admin_platform_treasury/utils.py

from datetime import datetime
from sqlalchemy import func
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from apps.utils.time_utils import format_full_timestamp

def get_ledger_summary(currency=None, start_date=None, end_date=None):
    """
    استخراج تقرير الأستاذ العام مع الفلترة الزمنية والعملة.
    """
    query = WalletTransaction.query.order_by(WalletTransaction.created_at.desc())

    # 1. فلترة العملة
    if currency and currency != 'all':
        query = query.filter(WalletTransaction.currency == currency)

    # 2. فلترة التاريخ والوقت (المرجع الزمني الموحد)
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(WalletTransaction.created_at >= start)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d 23:59:59')
        query = query.filter(WalletTransaction.created_at <= end)

    transactions = query.all()

    # 3. معالجة وتنسيق البيانات للعرض
    ledger_data = []
    for t in transactions:
        ledger_data.append({
            'voucher': t.voucher_number,
            'date': format_full_timestamp(t.created_at),  # التنسيق الموحد
            'type': t.trans_type,
            'amount': f"{t.amount} {t.currency}",
            'balance_after': t.balance_after,
            'description': t.description,
            'order_id': t.related_order_id
        })
        
    return ledger_data

def get_treasury_stats():
    """
    إحصائيات الخزينة العامة للمنصة.
    """
    stats = db.session.query(
        func.sum(SupplierWallet.balance_sar).label('total_sar'),
        func.sum(SupplierWallet.balance_usd).label('total_usd'),
        func.sum(SupplierWallet.balance_yer).label('total_yer')
    ).first()
    
    return {
        'total_sar': stats[0] or 0,
        'total_usd': stats[1] or 0,
        'total_yer': stats[2] or 0
    }
