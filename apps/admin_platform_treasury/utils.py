# 📂 apps/admin_platform_treasury/utils.py
from apps.models.wallet_db import WalletTransaction
from sqlalchemy import func

def get_treasury_stats(db):
    """حساب الأرصدة الكلية لكل عملة بشكل ديناميكي"""
    currencies = ['SAR', 'YER', 'USD']
    stats = {}
    
    for curr in currencies:
        stats[f'revenue_{curr.lower()}'] = db.session.query(func.sum(WalletTransaction.amount))\
            .filter(WalletTransaction.currency == curr, WalletTransaction.trans_type == 'platform_commission').scalar() or 0
        stats[f'payouts_{curr.lower()}'] = db.session.query(func.sum(WalletTransaction.amount))\
            .filter(WalletTransaction.currency == curr, WalletTransaction.trans_type == 'withdrawal').scalar() or 0
            
    return stats

def get_filtered_transactions(currency_filter=None):
    """تجهيز استعلام الحركات مع إمكانية الفلترة"""
    query = WalletTransaction.query.order_by(WalletTransaction.created_at.desc())
    
    if currency_filter and currency_filter != 'all':
        query = query.filter(WalletTransaction.currency == currency_filter)
        
    return query
