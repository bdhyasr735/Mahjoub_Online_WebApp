# coding: utf-8
"""
📂 apps/supplier_wallet/routes/wallet_routes.py
متحكم محفظة المورد الرئيسي (Supplier Wallet Flask Controller)
- عرض كشف الحساب وسندات الحركات المالية مع البحث المفهرس
- تقديم طلبات السحب المالي عبر POST المباشر (Zero-JS)
- إرسال التنبيهات الفورية (Toasts)
"""

from decimal import Decimal
from flask import render_template, request, redirect, url_for, g
from models.wallet_models import (
    SupplierWallet,
    WalletTransaction,
    WithdrawalRequest,
    VoucherReceipt
)
from models.bank_account_models import BankAccount
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.registry import supplier_wallet_bp


@supplier_wallet_bp.route('/', methods=['GET'])
def index():
    """التحويل المباشر للوحة القيادة"""
    return redirect(url_for('supplier_wallet.wallet_dashboard'))


@supplier_wallet_bp.route('/dashboard', methods=['GET'])
def wallet_dashboard():
    """لوحة القيادة الرئيسية وكشف الحساب لمحفظة المورد"""
    supplier_id = getattr(g, 'current_supplier_id', 9634)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    # معايير البحث والفلترة
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query_search = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if wallet:
        tx_query = WalletTransaction.query.filter_by(wallet_id=wallet.id)
        if query_search:
            tx_query = tx_query.filter(
                (WalletTransaction.description.ilike(f'%{query_search}%')) |
                (WalletTransaction.voucher_number.ilike(f'%{query_search}%')) |
                (WalletTransaction.reference_number.ilike(f'%{query_search}%')) |
                (WalletTransaction.transfer_number.ilike(f'%{query_search}%')) |
                (WalletTransaction.order_id.ilike(f'%{query_search}%')) |
                (WalletTransaction.approval_ref.ilike(f'%{query_search}%')) |
                (WalletTransaction.display_beneficiary.ilike(f'%{query_search}%')) |
                (WalletTransaction.display_bank.ilike(f'%{query_search}%'))
            )
        if trans_type:
            tx_query = tx_query.filter_by(trans_type=trans_type)
        if status:
            tx_query = tx_query.filter_by(status=status)

        pagination = tx_query.order_by(WalletTransaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        transactions_list = pagination.items
    else:
        pagination = None
        transactions_list = []

    return render_template(
        'supplier/wallet_transactions.html',
        wallet=wallet,
        transactions=transactions_list,
        pagination=pagination
    )


@supplier_wallet_bp.route('/transactions', methods=['GET'])
def transactions():
    """اسم مسار بديل لكشف الحساب"""
    return wallet_dashboard()


@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    """طلب سحب رصيد بنكي عبر نموذج POST فوري (Zero-JS)"""
    supplier_id = getattr(g, 'current_supplier_id', 9634)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    bank_accounts = BankAccount.query.filter_by(supplier_id=supplier_id).all()

    if request.method == 'POST':
        try:
            amount = Decimal(request.form.get('amount', '0'))
            bank_account_id = int(request.form.get('bank_account_id', 0))
            notes = request.form.get('notes', '').strip()

            from flask import current_app
            session = current_app.extensions['sqlalchemy'].db.session

            wdr = WalletService.create_withdrawal_request(
                session=session,
                wallet_id=wallet.id,
                bank_account_id=bank_account_id,
                amount=amount,
                notes=notes
            )
            session.commit()

            # إطلاق إشعار Toast فوري بنجاح تقديم طلب السحب
            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
            return redirect(url_for('supplier_wallet.wallet_dashboard'))

        except Exception as e:
            session.rollback()
            NotificationService.notify_error(str(e), title="فشل تقديم طلب السحب")

    return render_template(
        'supplier/withdrawal_form.html',
        wallet=wallet,
        bank_accounts=bank_accounts
    )
