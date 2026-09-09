# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/receipt_routes.py

from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.routes import supplier_wallet_bp, get_current_supplier_id, safe_redirect_home


@supplier_wallet_bp.route('/receipt/<string:request_number>', strict_slashes=False)
@login_required
def withdrawal_receipt(request_number):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    if not supplier_id:
        return safe_redirect_home()

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return safe_redirect_home()

    query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id)
    if request_number.isdigit():
        receipt = query.filter((WithdrawalRequest.request_number == request_number) | (WithdrawalRequest.id == int(request_number))).first_or_404()
    else:
        receipt = query.filter_by(request_number=request_number).first_or_404()

    supplier = Supplier.query.get(supplier_id) if hasattr(Supplier, 'query') else current_user

    # ✅ الحل النهائي: البحث عن الحركة المالية الصحيحة المرتبطة بالطلب
    transaction = None
    for txn in WalletTransaction.query.filter_by(wallet_id=wallet.id, transaction_type='withdraw').all():
        if receipt.request_number in txn.description:
            transaction = txn
            break

    # إذا لم نجد، نأخذ آخر حركة سحب
    if not transaction:
        transaction = WalletTransaction.query.filter_by(
            wallet_id=wallet.id,
            transaction_type='withdraw'
        ).order_by(WalletTransaction.created_at.desc()).first()

    return render_template(
        'supplier_wallet/withdrawal_receipt.html',
        receipt=receipt,
        req=receipt,
        withdrawal=receipt,
        wallet=wallet,
        supplier=supplier,
        transaction=transaction,
    )
