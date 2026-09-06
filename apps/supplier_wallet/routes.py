# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
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
from datetime import datetime

supplier_wallet_bp = Blueprint('supplier_wallet_bp', __name__, template_folder='templates', url_prefix='/supplier/wallet')

def get_wallet_balance(wallet):
    if not wallet:
        return Decimal('0.0')
    if hasattr(wallet, 'balance'):
        return Decimal(str(wallet.balance or 0.0))
    elif hasattr(wallet, 'balance_sar'):
        return Decimal(str(wallet.balance_sar or 0.0))
    elif hasattr(wallet, 'wallet_balance'):
        return Decimal(str(wallet.wallet_balance or 0.0))
    elif hasattr(wallet, 'amount'):
        return Decimal(str(wallet.amount or 0.0))
    else:
        print("⚠️ [تحذير]: لم يتم العثور على عمود الرصيد في SupplierWallet")
        return Decimal('0.0')

def get_sidebar_modules():
    supplier_modules = {}
    try:
        from apps.suppliers_dashboard.registry import MODULES_REGISTRY
        if MODULES_REGISTRY:
            supplier_modules = MODULES_REGISTRY.copy()
    except ImportError:
        pass
    if not supplier_modules and hasattr(current_app, 'supplier_modules') and current_app.supplier_modules:
        supplier_modules = current_app.supplier_modules.copy()
    if not supplier_modules:
        supplier_modules = {
            'financial_management': {
                'title': 'الإدارة المالية',
                'icon': 'fas fa-wallet',
                'links': {
                    'supplier_wallet_bp.wallet_dashboard_redirect': 'حركة المحفظة',
                    'supplier_wallet_bp.withdraw_redirect': 'سحب الرصيد'
                }
            }
        }
    return supplier_modules

def get_current_wallet_identifier():
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    if not supplier_id:
        return '1'
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

@supplier_wallet_bp.route('/transactions', strict_slashes=False)
@login_required
def transactions_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))

@supplier_wallet_bp.route('/withdraw', strict_slashes=False)
@login_required
def withdraw_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.withdraw', wallet_id=wallet_id))

@supplier_wallet_bp.route('/', strict_slashes=False)
@supplier_wallet_bp.route('/dashboard', strict_slashes=False)
@login_required
def wallet_dashboard_redirect():
    wallet_id = get_current_wallet_identifier()
    return redirect(url_for('supplier_wallet_bp.wallet_dashboard', wallet_id=wallet_id))

@supplier_wallet_bp.route('/<string:wallet_id>/', strict_slashes=False)
@supplier_wallet_bp.route('/<string:wallet_id>/dashboard', strict_slashes=False)
@login_required
def wallet_dashboard(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
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
    modules = get_sidebar_modules()
    return render_template(
        'supplier_wallet/dashboard.html',
        wallet=wallet,
        transactions=transactions,
        withdrawal_requests=withdrawal_requests,
        supplier_modules=modules,
        modules_registry=modules
    )

@supplier_wallet_bp.route('/<string:wallet_id>/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return redirect(url_for('supplier_wallet_bp.wallet_dashboard', wallet_id=wallet_id))
    current_balance = get_wallet_balance(wallet)
    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip().replace(',', '.')
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')
            if amount <= 0:
                raise ValueError("مبلغ السحب يجب أن يكون أكبر من الصفر")
            if amount > current_balance:
                raise ValueError("المبلغ المطلوب يتجاوز رصيد المحفظة المتاح")
            bank_account = request.form.get('bank_account_id', 'مصرف الراجحي - شركة الأناقة للتجارة')
            notes = request.form.get('notes', '')
            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()
            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
            return redirect(url_for('supplier_wallet_bp.withdraw', wallet_id=wallet_id))
        except ValueError as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal ValueError]: {str(e)}")
            NotificationService.notify_error(str(e), "خطأ في طلب السحب")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal Exception]: {str(e)}")
            traceback.print_exc()
            NotificationService.notify_error(f"حدث خطأ غير متوقع: {str(e)}", "خطأ نظام")
        return redirect(url_for('supplier_wallet_bp.withdraw', wallet_id=wallet_id))
    page = request.args.get('page', 1, type=int)
    query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).order_by(WithdrawalRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)
    active_bank = {
        'bank_name': 'مصرف الراجحي - شركة الأناقة للتجارة',
        'id': 1
    }
    modules = get_sidebar_modules()
    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        balance=current_balance,
        active_bank=active_bank,
        pagination=pagination,
        supplier_modules=modules,
        modules_registry=modules
    )

@supplier_wallet_bp.route('/receipt/<string:request_number>', strict_slashes=False)
@login_required
def withdrawal_receipt(request_number):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    if not supplier_id:
        return redirect(url_for('main.index'))
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return redirect(url_for('main.index'))
    receipt = WithdrawalRequest.query.filter_by(request_number=request_number, wallet_id=wallet.id).first_or_404()
    supplier = Supplier.query.get(supplier_id)
    modules = get_sidebar_modules()
    return render_template(
        'supplier_wallet/withdrawal_receipt.html',
        receipt=receipt,
        wallet=wallet,
        supplier=supplier,
        supplier_modules=modules,
        modules_registry=modules
    )

@supplier_wallet_bp.route('/<string:wallet_id>/transactions', strict_slashes=False)
@login_required
def transactions(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        return redirect(url_for('supplier_wallet_bp.wallet_dashboard', wallet_id=wallet_id))
    transactions_list = WalletTransaction.query.filter_by(wallet_id=wallet.id).all()
    withdrawal_requests = WithdrawalRequest.query.filter_by(wallet_id=wallet.id).all()
    all_transactions = list(transactions_list)
    for req in withdrawal_requests:
        all_transactions.append({
            'voucher_number': req.request_number,
            'reference_number': req.request_number,
            'transaction_type': 'debit',
            'amount': req.amount,
            'balance_after': None,
            'status': req.status,
            'created_at': req.created_at,
            'is_withdrawal': True
        })
    def get_sort_key(t):
        if isinstance(t, dict):
            return t.get('created_at') or datetime.min
        return getattr(t, 'created_at', datetime.min)
    all_transactions.sort(key=get_sort_key, reverse=True)
    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()
    if search_query:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                v_num = str(t.get('voucher_number', ''))
                r_num = str(t.get('reference_number', ''))
            else:
                v_num = str(getattr(t, 'voucher_number', ''))
                r_num = str(getattr(t, 'reference_number', ''))
            if search_query.lower() in v_num.lower() or search_query.lower() in r_num.lower():
                filtered_list.append(t)
        all_transactions = filtered_list
    if trans_type:
        filtered_list = []
        for t in all_transactions:
            t_type = t.get('transaction_type') if isinstance(t, dict) else getattr(t, 'transaction_type', None)
            if t_type == trans_type:
                filtered_list.append(t)
        all_transactions = filtered_list
    if status:
        filtered_list = []
        for t in all_transactions:
            s_val = t.get('status') if isinstance(t, dict) else getattr(t, 'status', None)
            if s_val == status:
                filtered_list.append(t)
        all_transactions = filtered_list
    balance = get_wallet_balance(wallet)
    modules = get_sidebar_modules()
    return render_template(
        'supplier_wallet/wallet_transactions.html',
        wallet=wallet,
        balance=balance,
        transactions=all_transactions,
        supplier_modules=modules,
        modules_registry=modules,
        now=datetime.now()
    )

@supplier_wallet_bp.route('/store/<string:supplier_code>', strict_slashes=False)
def public_store_view(supplier_code):
    supplier = Supplier.query.filter_by(supplier_code=supplier_code, status='active').first_or_404()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    modules = get_sidebar_modules()
    return render_template(
        'supplier_wallet/public_store.html',
        supplier=supplier,
        wallet=wallet,
        supplier_modules=modules,
        modules_registry=modules
    )
