# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, session, abort
from flask_login import login_required
from sqlalchemy import func

# الاستيرادات الضرورية التي كانت ناقصة
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier 

# 1. تعريف البلوبرينت
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

def admin_required():
    """التحقق من صلاحية المدير."""
    if session.get('user_type') != 'admin':
        abort(403)

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    admin_required()
    
    # 1. حساب الإحصائيات
    total_suppliers = Supplier.query.count() or 0
    
    # 2. حساب الأرصدة (باستخدام db المستورد)
    stats = db.session.query(
        func.sum(SupplierWallet.balance_sar),
        func.sum(SupplierWallet.balance_yer),
        func.sum(SupplierWallet.balance_usd)
    ).first()
    
    # 3. جلب آخر 10 عمليات
    recent_transactions = WalletTransaction.query.order_by(
        WalletTransaction.created_at.desc()
    ).limit(10).all()
    
    context = {
        'total_suppliers': total_suppliers,
        'total_balance_sar': stats[0] or 0.00,
        'total_balance_yer': stats[1] or 0.00,
        'total_balance_usd': stats[2] or 0.00,
        'recent_transactions': recent_transactions
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_dashboard.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    admin_required()
    return render_template('admin/settings.html')
