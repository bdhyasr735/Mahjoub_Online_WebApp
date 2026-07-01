# coding: utf-8
# 📂 apps/admin_financial_management/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from sqlalchemy import func

# تعريف البلوبرنت الخاص بإدارة المالية
financial_mgmt_bp = Blueprint(
    'financial_mgmt_bp', 
    __name__, 
    template_folder='templates'
)

@financial_mgmt_bp.route('/dashboard', methods=['GET'])
@login_required
def financial_dashboard():
    """لوحة التحكم المالية: كشف حساب دائن ومدين مع الترقيم والفلترة."""
    
    # 1. إعدادات الفلترة والترقيم
    currency = request.args.get('currency', 'SAR')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 2. استعلام أساسي مفلتر بالعملة
    base_query = WalletTransaction.query.filter_by(currency=currency)
    
    # 3. حساب الملخصات المالية
    total_credit = db.session.query(func.sum(WalletTransaction.amount))\
        .filter_by(currency=currency)\
        .filter(WalletTransaction.trans_type.in_(['platform_commission', 'sale_revenue', 'adjustment_credit'])).scalar() or 0.00
        
    total_debit = db.session.query(func.sum(WalletTransaction.amount))\
        .filter_by(currency=currency)\
        .filter(WalletTransaction.trans_type.in_(['marketer_commission', 'adjustment_debit'])).scalar() or 0.00
    
    # 4. الترقيم (Pagination)
    pagination = base_query.order_by(WalletTransaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 5. تجهيز البيانات للعرض
    processed_transactions = []
    for t in pagination.items:
        is_credit = t.trans_type in ['platform_commission', 'sale_revenue', 'adjustment_credit']
        processed_transactions.append({
            'created_at': t.created_at,
            'description': t.description or t.trans_type,
            'related_order_id': getattr(t, 'order_id', None),
            'debit': t.amount if not is_credit else 0.00,
            'credit': t.amount if is_credit else 0.00,
            'balance_after': t.balance_after # الرصيد التراكمي المهم لكشف الحساب
        })

    return render_template(
        'admin_financial_management.html',
        transactions=processed_transactions,
        total_credit=float(total_credit),
        total_debit=float(total_debit),
        net_profit=float(total_credit - total_debit),
        pagination=pagination,
        active_currency=currency
    )

def register_module(app):
    """تسجيل موديول الإدارة المالية في التطبيق."""
    app.register_blueprint(financial_mgmt_bp, url_prefix='/admin/financial-management')
