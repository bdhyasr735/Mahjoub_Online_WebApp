# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr
import re
import traceback
from decimal import Decimal

# ✅ تعريف الـ Blueprint بنفس اسم الـ LINKS في registry.py
wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates', url_prefix='/supplier/wallet')

# ✅ Context Processor مباشر
@wallet_bp.context_processor
def inject_supplier_modules():
    """حقن الموديولات في القائمة الجانبية"""
    supplier_modules = {}
    if hasattr(current_app, 'supplier_modules'):
        supplier_modules = current_app.supplier_modules.copy()
    return {'supplier_modules': supplier_modules}


def get_current_wallet_identifier():
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        return 'general'
    
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if wallet:
        if hasattr(wallet, 'wallet_code') and wallet.wallet_code:
            return str(wallet.wallet_code)
        return str(wallet.id)
        
    trade_name = getattr(current_user, 'trade_name', None)
    if trade_name:
        slug = re.sub(r'[^\w\s-]', '', trade_name).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        if slug:
            return slug
            
    return str(supplier_id)


@wallet_bp.route('/')
@wallet_bp.route('/dashboard')
@login_required
def wallet_dashboard_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))


@wallet_bp.route('/<string:wallet_id>/')
@wallet_bp.route('/<string:wallet_id>/dashboard')
@login_required
def wallet_dashboard(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        return redirect(url_for('main.index'))
    
    try:
        wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Wallet Dashboard Error]: {str(e)}")
        traceback.print_exc()
        return redirect(url_for('main.index'))

    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc()).all()
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc()).all()

    return render_template(
        'supplier_wallet/dashboard.html',
        wallet=wallet,
        transactions=transactions,
        withdrawal_requests=withdrawal_requests
    )


@wallet_bp.route('/<string:wallet_id>/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw(wallet_id):
    """عرض نموذج السحب ومعالجته"""
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))

    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip().replace(',', '.')
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')
            
            if amount <= 0:
                raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
                
            if amount > wallet.balance_sar:
                raise ValueError("المبلغ المطلوب يتجاوز رصيد المحفظة المتاح")

            bank_account = request.form.get('bank_account_id', 'مصرف الراجحي - شركة الأناقة للتجارة')
            notes = request.form.get('notes', '')

            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()

            return redirect(url_for('supplier_wallet.withdraw', wallet_id=wallet_id, success='true'))
            
        except ValueError as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal ValueError]: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal Exception]: {str(e)}")
            traceback.print_exc()

        return redirect(url_for('supplier_wallet.withdraw', wallet_id=wallet_id))

    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    active_bank = {
        'bank_name': 'مصرف الراجحي - شركة الأناقة للتجارة',
        'id': 1
    }

    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        active_bank=active_bank,
        pagination=pagination
    )


@wallet_bp.route('/receipt/<string:request_number>')
@login_required
def withdrawal_receipt(request_number):
    supplier_id = get_current_supplier_id()
    if not supplier_id:
        return redirect(url_for('main.index'))

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return redirect(url_for('main.index'))

    receipt = WithdrawalRequest.query.filter_by(request_number=request_number, wallet_id=wallet.id).first_or_404()
    supplier = Supplier.query.get(supplier_id)

    # ✅ تمرير الموديولات لضمان ظهور القائمة الجانبية كاملة في صفحة السند
    supplier_modules = {}
    if hasattr(current_app, 'supplier_modules'):
        supplier_modules = current_app.supplier_modules.copy()

    return render_template(
        'supplier_wallet/withdrawal_receipt.html',
        receipt=receipt,
        wallet=wallet,
        supplier=supplier,
        supplier_modules=supplier_modules
    )


@wallet_bp.route('/<string:wallet_id>/transactions')
@login_required
def transactions(wallet_id):
    """عرض كشف الحساب"""
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    if not wallet:
        return redirect(url_for('supplier_wallet.wallet_dashboard', wallet_id=wallet_id))

    query = WalletTransaction.query.filter_by(wallet_id=wallet.id)

    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if search_query:
        query = query.filter(
            db.or_(
                WalletTransaction.voucher_number.ilike(f'%{search_query}%'),
                WalletTransaction.transfer_number.ilike(f'%{search_query}%'),
                WalletTransaction.reference_number.ilike(f'%{search_query}%')
            )
        )

    trx_column = get_trx_type_attr()
    if trans_type and trx_column is not None:
        query = query.filter(trx_column == trans_type)

    if status and hasattr(WalletTransaction, 'status'):
        query = query.filter_by(status=status)

    transactions = query.order_by(WalletTransaction.created_at.desc()).all()

    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        transactions=transactions
    )


@wallet_bp.route('/store/<string:supplier_code>')
def public_store_view(supplier_code):
    supplier = Supplier.query.filter_by(supplier_code=supplier_code, status='active').first_or_404()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    return render_template(
        'supplier_wallet/public_store.html',
        supplier=supplier,
        wallet=wallet
    )
