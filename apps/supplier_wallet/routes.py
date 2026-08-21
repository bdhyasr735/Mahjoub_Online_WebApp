# coding: utf-8
"""
📂 apps/supplier_wallet/routes.py
مسارات واجهات محفظة المورد (Supplier Wallet Routes)
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from decimal import Decimal

wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates', url_prefix='/supplier/wallet')


@wallet_bp.route('/')
@login_required
def wallet_dashboard():
    """لوحة تحكم المحفظة الخاصة بالمورد"""
    supplier_id = getattr(current_user, 'supplier_id', None) or getattr(current_user, 'id', None)
    
    # جلب المحفظة أو إنشائها تلقائياً للمورد الحالي
    wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
    db.session.commit()

    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc()).all()

    return render_template(
        'supplier_wallet/dashboard.html',
        wallet=wallet,
        transactions=transactions,
        withdrawal_requests=withdrawal_requests
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """عرض نموذج السحب (GET) ومعالجة طلب السحب (POST)"""
    supplier_id = getattr(current_user, 'supplier_id', None) or getattr(current_user, 'id', None)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        NotificationService.notify_error("المحفظة غير موجودة")
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    if request.method == 'POST':
        try:
            amount = Decimal(request.form.get('amount', '0'))
            # استقبال جهة التحويل أو الحساب البنكي المسجل تلقائياً
            bank_account = request.form.get('bank_account_id', getattr(wallet, 'bank_name', 'الحساب البنكي المعتمد للمتجر'))
            notes = request.form.get('notes', '')

            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()

            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
        except ValueError as e:
            db.session.rollback()
            NotificationService.notify_error(str(e))
        except Exception as e:
            db.session.rollback()
            NotificationService.notify_error("حدث خطأ غير متوقع أثناء معالجة طلب السحب")

        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    # تمرير المحفظة وجهة التحويل للقالب
    return render_template('supplier_wallet/withdrawal_form.html', wallet=wallet)


@wallet_bp.route('/transactions')
@login_required
def transactions():
    """عرض كشف الحساب وسندات الحركات المالية مع الفلترة (Zero-JS)"""
    supplier_id = getattr(current_user, 'supplier_id', None) or getattr(current_user, 'id', None)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    query = WalletTransaction.query.filter_by(wallet_id=wallet.id)

    # استقبال معاملات الفلترة عبر الرابط (GET Parameters)
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if search_query:
        query = query.filter(
            db.or_(
                WalletTransaction.voucher_number.ilike(f'%{search_query}%'),
                WalletTransaction.transfer_number.ilike(f'%{search_query}%'),
                WalletTransaction.reference_number.ilike(f'%{search_query}%'),
                WalletTransaction.description.ilike(f'%{search_query}%')
            )
        )

    if trans_type:
        query = query.filter_by(trans_type=trans_type)

    if status:
        query = query.filter_by(status=status)

    transactions = query.order_by(WalletTransaction.created_at.desc()).all()

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        transactions=transactions
    )
