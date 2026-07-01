# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.wallet_db import WalletTransaction, SupplierWallet
from sqlalchemy import func

# تعريف البلوبرنت
treasury_bp = Blueprint(
    'treasury_bp', 
    __name__, 
    template_folder='templates'
)

@treasury_bp.route('/', methods=['GET'])
@login_required
def index():
    """عرض الأستاذ العام (كشف حساب المنصة)."""
    
    # 1. جلب كافة الحركات المالية بترتيب زمني تنازلي
    # ملاحظة: نحن نقوم بجلب البيانات وتصنيفها إلى مدين ودائن في كائن النتيجة
    query = WalletTransaction.query.order_by(WalletTransaction.created_at.desc())
    transactions = query.all()

    # 2. تحضير الحركات للعرض (المدين والدائن)
    processed_transactions = []
    for t in transactions:
        # تحديد المدين والدائن بناءً على نوع الحركة
        # المدين (Debit): المبالغ التي تُخصم من الرصيد
        # الدائن (Credit): المبالغ التي تضاف للرصيد
        is_credit = t.trans_type in ['credit', 'adjustment_credit', 'sale_revenue']
        
        t.debit = 0.00 if is_credit else t.amount
        t.credit = t.amount if is_credit else 0.00
        
        processed_transactions.append(t)

    # 3. حساب إجمالي رصيد الخزينة (الرصيد الأخير في آخر حركة)
    last_trans = WalletTransaction.query.order_by(WalletTransaction.id.desc()).first()
    total_balance = last_trans.balance_after if last_trans else 0.00

    return render_template(
        'admin_platform_treasury.html',
        transactions=processed_transactions,
        total_balance=total_balance
    )

@treasury_bp.route('/filter', methods=['GET'])
@login_required
def filter_treasury():
    """دالة إضافية للبحث المتقدم (اختياري)"""
    voucher = request.args.get('voucher')
    if voucher:
        transactions = WalletTransaction.query.filter(
            WalletTransaction.voucher_number.like(f"%{voucher}%")
        ).all()
        # (يمكن هنا إضافة منطق حساب الأرصدة المفلترة)
        return render_template('admin_platform_treasury.html', transactions=transactions)
    return index()
