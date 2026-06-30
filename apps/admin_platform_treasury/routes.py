# coding: utf-8
from flask import render_template
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from sqlalchemy import func
from . import treasury_bp # تأكد أن هذا هو نفس الاسم المستخدم عند التسجيل في __init__.py

@treasury_bp.route('/dashboard', methods=['GET'])
@login_required
def treasury_dashboard():
    """
    لوحة تحكم خزينة المنصة
    المسار النهائي بعد تسجيل الـ Blueprint سيكون: /admin/treasury/dashboard
    """
    # 1. إجمالي ما دخل للمنصة (العمولات فقط)
    total_revenue = db.session.query(func.sum(WalletTransaction.amount))\
        .filter(WalletTransaction.trans_type == 'platform_commission').scalar() or 0
        
    # 2. إجمالي ما تم تحويله للموردين
    total_payouts = db.session.query(func.sum(WalletTransaction.amount))\
        .filter(WalletTransaction.trans_type == 'withdrawal').scalar() or 0
        
    # 3. آخر الحركات المالية للتدقيق
    transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).limit(100).all()
    
    return render_template('admin/treasury/admin_platform_treasury.html',
                           total_revenue=abs(float(total_revenue)),
                           total_payouts=abs(float(total_payouts)),
                           transactions=transactions)
