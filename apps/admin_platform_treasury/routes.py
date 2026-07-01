# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.wallet_db import WalletTransaction
from sqlalchemy import func

# تعريف البلوبرنت
treasury_bp = Blueprint(
    'treasury_bp', 
    __name__, 
    template_folder='templates'
)

@treasury_bp.route('/dashboard', methods=['GET'])
@login_required
def index():
    """عرض الأستاذ العام (كشف حساب المنصة)."""
    
    # 1. جلب كافة الحركات المالية بترتيب زمني تنازلي
    transactions = WalletTransaction.query.order_by(WalletTransaction.created_at.desc()).all()

    # 2. تحضير الحركات للعرض (استخدام قاموس لتجنب أخطاء SQLAlchemy)
    processed_transactions = []
    for t in transactions:
        # تحديد نوع الحركة
        is_credit = t.trans_type in ['credit', 'adjustment_credit', 'sale_revenue']
        
        # إنشاء قاموس يحتوي على البيانات لعرضها في القالب
        # هذا يحل مشكلة 'invalid keyword argument' لأننا لا نعدل كائن قاعدة البيانات
        tx_data = {
            'voucher_number': t.voucher_number,
            'created_at': t.created_at,
            'description': t.description,
            'amount': t.amount,
            'balance_after': t.balance_after,
            'debit': 0.00 if is_credit else t.amount,
            'credit': t.amount if is_credit else 0.00
        }
        processed_transactions.append(tx_data)

    # 3. حساب إجمالي رصيد الخزينة (الرصيد الأخير)
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
    """دالة البحث المتقدم"""
    voucher = request.args.get('voucher')
    if voucher:
        # ملاحظة: في حال البحث، يفضل أيضاً تحويل البيانات لقواميس بنفس الطريقة المذكورة أعلاه
        transactions = WalletTransaction.query.filter(
            WalletTransaction.voucher_number.like(f"%{voucher}%")
        ).all()
        return render_template('admin_platform_treasury.html', transactions=transactions)
    return index()
