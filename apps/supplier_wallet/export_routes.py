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
    get_or_create_supplier_wallet
)

@supplier_wallet_bp.route('/wallet/export-pdf', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/withdraw/export-pdf', methods=['GET'], strict_slashes=False)
@login_required
def export_wallet_pdf():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # تجهيز الملخص مباشرة من خصائص الموديل المحفوظة
    summary = {
        'total_balance': float(wallet_obj.balance_sar or 0.0) if wallet_obj else 0.0,
        'available_balance': float(wallet_obj.balance_sar or 0.0) if wallet_obj else 0.0,
        'pending_balance': float(wallet_obj.balance_pending or 0.0) if wallet_obj else 0.0,
        'total_withdrawn': float(wallet_obj.total_withdrawn or 0.0) if wallet_obj else 0.0,
        'currency': 'SAR'
    }

    # تحديد الاستعلام بناءً على الرابط (محفظة عامة أم طلبات سحب)
    is_withdraw_path = 'withdraw' in request.path
    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    if is_withdraw_path:
        query = query.filter(WalletTransaction.trans_type == 'withdrawal')
    else:
        # فلاتر المحفظة العامة
        trx_type = request.args.get('type', 'all')
        if trx_type != 'all':
            query = query.filter(WalletTransaction.trans_type == trx_type)

    # فلترة الحالة
    status = request.args.get('status', 'all')
    if status != 'all':
        query = query.filter(WalletTransaction.status == status)
    elif not is_withdraw_path:
        # افتراضياً في طباعة المحفظة العامة نأخذ غير المعلقة أو المكتملة بناءً على رغبة النظام
        query = query.filter(WalletTransaction.status != 'pending')

    transactions = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc()).all()

    return render_template(
        'supplier_wallet/wallet_pdf_print.html',
        summary=summary,
        transactions=transactions,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
