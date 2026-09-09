# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/print_routes.py

from flask import render_template, request
from flask_login import login_required, current_user

from decimal import Decimal
from datetime import datetime

from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.routes import supplier_wallet_bp, get_current_supplier_id, safe_redirect_home


@supplier_wallet_bp.route('/<string:wallet_id>/print', methods=['GET'])
@login_required
def print_wallet_transactions(wallet_id):
    """طباعة كشف حساب المحفظة المالية بشكل نظيف ومستقل"""
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        return safe_redirect_home()

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return safe_redirect_home()

    supplier = Supplier.query.filter_by(id=supplier_id).first()

    # ✅ تطبيق فلاتر الفترة (اختياري)
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    query = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc())

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            query = query.filter(WalletTransaction.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(WalletTransaction.created_at <= end_dt)
        except ValueError:
            pass

    transactions = query.all()

    # ✅ حساب الرصيد بعد كل حركة
    running_balance = Decimal(str(wallet.balance))
    for trx in reversed(transactions):
        trx.balance_after = running_balance
        if trx.transaction_type in ['credit', 'deposit']:
            running_balance = running_balance - Decimal(str(trx.amount))
        elif trx.transaction_type in ['debit', 'withdraw']:
            running_balance = running_balance + Decimal(str(trx.amount))

    return render_template(
        'supplier_wallet/print_wallet_transactions.html',
        wallet=wallet,
        supplier=supplier,
        transactions=transactions,
        now=datetime.now()
    )
