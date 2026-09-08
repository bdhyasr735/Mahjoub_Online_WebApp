# coding: utf-8
# 📂 apps/wallet/withdrawals.py
import logging
from datetime import datetime
from decimal import Decimal

from flask import render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest, generate_unique_voucher_number
from apps.models.supplier_db import Supplier
from apps.models.treasury_db import TreasuryEntry
from apps.wallet.routes import wallet_bp

logger = logging.getLogger(__name__)

# استيراد البنوك والشركات
try:
    from apps.data.yemen_banks import BANKS_LIST
except ImportError:
    BANKS_LIST = []
try:
    from apps.data.financial_companies import COMPANIES_LIST
except ImportError:
    COMPANIES_LIST = []

@wallet_bp.route('/admin/withdrawals', methods=['GET'])
@login_required
def admin_withdrawals():
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.join(SupplierWallet, WithdrawalRequest.wallet_id == SupplierWallet.id).join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            WithdrawalRequest.request_number.ilike(f'%{search}%'),
            WithdrawalRequest.status.ilike(f'%{search}%')
        ))
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    stats = {
        'pending': WithdrawalRequest.query.filter_by(status='pending').count(),
        'completed': WithdrawalRequest.query.filter_by(status='completed').count(),
        'rejected': WithdrawalRequest.query.filter_by(status='rejected').count(),
    }
    pagination = query.order_by(WithdrawalRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/withdrawals_table_body.html', requests=pagination.items, pagination=pagination)
    return render_template('admin/withdrawals_list.html', requests=pagination.items, stats=stats, pagination=pagination, status_filter=status_filter)

@wallet_bp.route('/admin/withdrawals/<string:request_number>', methods=['GET'])
@login_required
def admin_view_withdrawal(request_number):
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    return render_template('admin/review_withdrawal.html', withdrawal=withdrawal, banks=BANKS_LIST, companies=COMPANIES_LIST)

@wallet_bp.route('/admin/withdrawals/<string:request_number>/approve', methods=['POST'])
@login_required
def approve_withdrawal(request_number):
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    wallet = withdrawal.wallet
    if withdrawal.status != 'pending':
        flash("لا يمكن تعديل هذا الطلب لأن حالته ليست قيد الانتظار.", "warning")
        return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))
    try:
        bank_name = request.form.get('bank_name', '').strip()
        transfer_company = request.form.get('transfer_company', '').strip()
        bank_reference = request.form.get('bank_reference', '').strip()
        admin_notes = request.form.get('admin_notes', '').strip()
        withdrawal.status = 'completed'
        withdrawal.updated_at = datetime.utcnow()
        withdrawal.notes = admin_notes if admin_notes else 'تمت الموافقة على السحب'
        wallet.balance = Decimal(wallet.balance) - Decimal(withdrawal.amount)
        wallet.total_withdrawn = Decimal(wallet.total_withdrawn) + Decimal(withdrawal.amount)
        wallet.updated_at = datetime.utcnow()
        generated_voucher = generate_unique_voucher_number()
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=withdrawal.amount,
            transaction_type='withdraw',
            voucher_number=generated_voucher,
            bank_reference=bank_reference if bank_reference else None,
            transfer_company=transfer_company if transfer_company else None,
            description=f"سحب رصيد - طلب رقم: {withdrawal.request_number} | الجهة: {transfer_company or 'غير محدد'} | رقم الحوالة: {bank_reference or 'غير محدد'}"
        )
        db.session.add(transaction)
        db.session.add(wallet)
        db.session.add(withdrawal)
        treasury_voucher = generate_unique_voucher_number()
        treasury_entry = TreasuryEntry(
            reference_number=bank_reference if bank_reference else None,
            voucher_number=treasury_voucher,
            entry_type='withdraw',
            amount=withdrawal.amount,
            currency='SAR',
            owner_type='supplier',
            owner_id=withdrawal.supplier_id,
            description=f"سحب رصيد المورد - طلب رقم: {withdrawal.request_number}"
        )
        db.session.add(treasury_entry)
        db.session.commit()
        flash("تم اعتماد طلب السحب وخصم المبلغ من المحفظة بنجاح.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Withdrawal Approve Error: {e}")
        flash("حدث خطأ أثناء اعتماد الطلب.", "danger")
    return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))

@wallet_bp.route('/admin/withdrawals/<string:request_number>/reject', methods=['POST'])
@login_required
def reject_withdrawal(request_number):
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    if withdrawal.status != 'pending':
        flash("لا يمكن تعديل هذا الطلب لأن حالته ليست قيد الانتظار.", "warning")
        return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))
    try:
        withdrawal.status = 'rejected'
        withdrawal.updated_at = datetime.utcnow()
        db.session.add(withdrawal)
        db.session.commit()
        flash("تم رفض طلب السحب. المبلغ لم يتم خصمه من المحفظة.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Withdrawal Reject Error: {e}")
        flash("حدث خطأ أثناء رفض الطلب.", "danger")
    return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))
