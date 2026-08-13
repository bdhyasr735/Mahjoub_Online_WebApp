# coding: utf-8
# 📂 apps/supplier_wallet/export_routes.py

from datetime import datetime
from flask import render_template, request
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_trx_type_attr, 
    get_status_attr
)

@supplier_wallet_bp.route('/wallet/export-pdf', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/withdraw/export-pdf', methods=['GET'], strict_slashes=False)
@login_required
def export_wallet_pdf():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    summary = {'currency': getattr(wallet_obj, 'currency', 'SAR') if wallet_obj else 'SAR'}
    
    if wallet_obj:
        wallet_id = wallet_obj.id
        
        # حساب الملخصات المالية لنفس الكشف
        q_completed = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_completed = q_completed.filter(status_col == 'completed')
        if trx_type_col is not None:
            q_completed = q_completed.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit']))
        completed_credits = q_completed.scalar() or 0.00

        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_pending = q_pending.filter(status_col == 'pending')
        if trx_type_col is not None:
            q_pending = q_pending.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit', 'withdrawal', 'debit']))
        pending_credits = q_pending.scalar() or 0.00

        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_withdrawn = q_withdrawn.filter(status_col == 'completed')
        if trx_type_col is not None:
            q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = q_withdrawn.scalar() or 0.00

        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            avail_bal = max(0.00, float(getattr(wallet_obj, 'balance_sar', 0.00)))

        tot_bal = avail_bal + float(pending_credits)

        summary.update({
            'total_balance': float(tot_bal),
            'available_balance': float(avail_bal),
            'pending_balance': float(pending_credits),
            'total_withdrawn': float(total_withdrawn),
        })

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    if 'withdraw' in request.path:
        if trx_type_col is not None:
            query = query.filter(trx_type_col.in_(['withdrawal', 'debit']))

    trx_type = request.args.get('type', 'all')
    if trx_type != 'all' and trx_type_col is not None and 'withdraw' not in request.path:
        query = query.filter(trx_type_col == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all' and status_col is not None:
        query = query.filter(status_col == status)
    elif status_col is not None and 'withdraw' not in request.path:
        query = query.filter(status_col == 'completed')

    transactions = query.order_by(WalletTransaction.id.desc()).all()

    return render_template(
        'supplier_wallet/wallet_pdf_print.html',
        summary=summary,
        transactions=transactions,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
