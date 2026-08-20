# -*- coding: utf-8 -*-
"""
📂 apps/supplier_wallet/__init__.py
إدارة موديول محفظة المورد - منصة محجوب أونلاين
"""

from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models import BankAccount
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id

# تعريف الـ Blueprint الأساسي للمحفظة
supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@supplier_wallet_bp.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('supplier_wallet.wallet_dashboard'))

@supplier_wallet_bp.route('/dashboard', methods=['GET'])
@login_required
def wallet_dashboard():
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        flash('تعذر تحديد حساب المورد الحالي.', 'error')
        return redirect(url_for('suppliers_auth.login'))

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    # معايير البحث والفلترة
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query_search = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    tx_query = WalletTransaction.query.filter_by(wallet_id=wallet.id) if wallet else WalletTransaction.query.filter(False)

    if query_search:
        tx_query = tx_query.filter(
            (WalletTransaction.description.ilike(f'%{query_search}%')) |
            (WalletTransaction.voucher_number.ilike(f'%{query_search}%'))
        )
    if trans_type: tx_query = tx_query.filter_by(trans_type=trans_type)
    if status: tx_query = tx_query.filter_by(status=status)

    pagination = tx_query.order_by(WalletTransaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        transactions=pagination.items,
        pagination=pagination
    )

@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    bank_accounts = BankAccount.query.filter_by(supplier_id=supplier_id).all()

    if request.method == 'POST':
        try:
            amount = Decimal(request.form.get('amount', '0'))
            bank_account_id = int(request.form.get('bank_account_id', 0))
            notes = request.form.get('notes', '').strip()

            wdr = WalletService.create_withdrawal_request(
                session=db.session,
                wallet_id=wallet.id,
                bank_account_id=bank_account_id,
                amount=amount,
                notes=notes
            )
            db.session.commit()
            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
            flash('تم تقديم طلب السحب بنجاح.', 'success')
            return redirect(url_for('supplier_wallet.wallet_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'فشل تقديم طلب السحب: {str(e)}', 'error')

    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        bank_accounts=bank_accounts
    )
