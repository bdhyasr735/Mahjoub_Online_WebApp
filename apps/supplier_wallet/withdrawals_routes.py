# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/receipt_routes.py

from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WithdrawalRequest
from apps.supplier_wallet.routes import supplier_wallet_bp, get_current_supplier_id, safe_redirect_home


@supplier_wallet_bp.route('/<string:wallet_id>/receipt/<string:request_number>', methods=['GET'])
@login_required
def withdrawal_receipt(wallet_id, request_number):
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        return safe_redirect_home()

    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number, wallet_id=wallet_id).first()
    if not withdrawal:
        flash('لم يتم العثور على طلب السحب.', 'danger')
        return redirect(url_for('supplier_wallet_bp.process_withdraw', wallet_id=wallet_id))

    wallet = SupplierWallet.query.filter_by(id=withdrawal.wallet_id).first()
    supplier = wallet.supplier if wallet else None

    return render_template(
        'supplier_wallet/withdrawal_receipt.html',
        withdrawal_request=withdrawal,
        wallet=wallet,
        supplier=supplier
    )
