# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from sqlalchemy import func
from datetime import datetime

treasury_bp = Blueprint('treasury', __name__, template_folder='templates')

@treasury_bp.route('/dashboard', methods=['GET'])
@login_required
def treasury_dashboard():
    # دالة مساعدة لحساب الإجماليات حسب العملة والنوع
    def get_total(curr, t_type):
        return db.session.query(func.sum(WalletTransaction.amount))\
            .filter(WalletTransaction.currency == curr)\
            .filter(WalletTransaction.trans_type == t_type).scalar() or 0

    # تجميع البيانات للبطاقات العلوية
    stats = {
        'revenue_sar': get_total('SAR', 'platform_commission'),
        'payouts_sar': get_total('SAR', 'withdrawal'),
        'revenue_yer': get_total('YER', 'platform_commission'),
        'payouts_yer': get_total('YER', 'withdrawal'),
        'revenue_usd': get_total('USD', 'platform_commission'),
        'payouts_usd': get_total('USD', 'withdrawal')
    }
    
    # جلب كافة الحركات (الأستاذ العام)
    transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).all()
    
    return render_template('admin_platform_treasury.html', 
                           stats=stats, 
                           transactions=transactions,
                           now=datetime.now().strftime('%Y-%m-%d %H:%M'))
