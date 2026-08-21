# coding: utf-8
"""
📂 apps/supplier_wallet/routes.py
مسارات واجهات محفظة المورد (Supplier Wallet Routes)
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
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


@wallet_bp.route('/withdraw', methods=['POST'])
@login_required
def request_withdrawal():
    """معالجة طلب سحب أرباح جديد من المورد"""
    supplier_id = getattr(current_user, 'supplier_id', None) or getattr(current_user, 'id', None)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        NotificationService.notify_error("المحفظة غير موجودة")
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    try:
        amount = Decimal(request.form.get('amount', '0'))
        bank_account = request.form.get('bank_account_id', 'التحويل العام')
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
