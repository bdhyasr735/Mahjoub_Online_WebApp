# 📂 apps/admin_platform_treasury/routes.py

from flask import render_template
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import func
from . import treasury_bp

@treasury_bp.route('/admin/treasury/dashboard', methods=['GET'])
@login_required
def treasury_dashboard():
    """كشف حساب المنصة العام."""
    
    # حساب الإجمالي من المحافظ (كعرض لقوة السيولة)
    total_liquidity = db.session.query(func.sum(SupplierWallet.balance_yer)).scalar() or 0
    
    # حساب إجمالي العمليات (الداخل والخارج)
    total_in = db.session.query(func.sum(WalletTransaction.amount)).filter(WalletTransaction.amount > 0).scalar() or 0
    total_out = db.session.query(func.sum(WalletTransaction.amount)).filter(WalletTransaction.amount < 0).scalar() or 0
    
    # جلب آخر الحركات المالية ليعمل ككشف حساب
    recent_transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).limit(50).all()
    
    return render_template('admin/treasury/treasury_dashboard.html', 
                           total_liquidity=total_liquidity,
                           total_in=total_in,
                           total_out=abs(total_out),
                           transactions=recent_transactions)
