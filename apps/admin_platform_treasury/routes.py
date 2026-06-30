# coding: utf-8
from flask import render_template
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from sqlalchemy import func
from . import treasury_bp

@treasury_bp.route('/admin/treasury/dashboard')
@login_required
def treasury_dashboard():
    # 1. إجمالي ما دخل للمنصة (العمولات فقط)
    total_revenue = db.session.query(func.sum(WalletTransaction.amount))\
        .filter(WalletTransaction.trans_type == 'platform_commission').scalar() or 0
        
    # 2. إجمالي ما تم تحويله للموردين
    total_payouts = db.session.query(func.sum(WalletTransaction.amount))\
        .filter(WalletTransaction.trans_type == 'withdrawal').scalar() or 0
        
    # 3. آخر الحركات المالية للتدقيق
    transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).limit(100).all()
    
    return render_template('admin/treasury/admin_platform_treasury.html',
                           total_revenue=abs(total_revenue),
                           total_payouts=abs(total_payouts),
                           transactions=transactions)
