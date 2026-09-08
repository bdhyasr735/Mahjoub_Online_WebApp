# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/routes.py

import re
import traceback
import importlib
from decimal import Decimal
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.routing import BuildError

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest
from apps.models.supplier_db import Supplier
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id, get_trx_type_attr

supplier_wallet_bp = Blueprint('supplier_wallet_bp', __name__, template_folder='templates', url_prefix='/supplier/wallet')


def safe_redirect_home():
    """إعادة توجيه آمنة عند الفشل لتجنب خطأ BuildError."""
    try:
        return redirect(url_for('main.index'))
    except BuildError:
        try:
            return redirect(url_for('suppliers_dashboard.index'))
        except BuildError:
            return redirect('/')


def get_wallet_balance(wallet):
    """جلب رصيد المحفظة الإجمالي."""
    if not wallet:
        return Decimal('0.0')
    if hasattr(wallet, 'balance') and wallet.balance is not None:
        return Decimal(str(wallet.balance))
    elif hasattr(wallet, 'balance_sar') and wallet.balance_sar is not None:
        return Decimal(str(wallet.balance_sar))
    elif hasattr(wallet, 'wallet_balance') and wallet.wallet_balance is not None:
        return Decimal(str(wallet.wallet_balance))
    elif hasattr(wallet, 'amount') and wallet.amount is not None:
        return Decimal(str(wallet.amount))
    else:
        return Decimal('0.0')


def get_sidebar_modules():
    """تجميع موديولات القائمة الجانبية للمورد ديناميكياً لتشمل جميع الموديولات المتاحة."""
    supplier_modules = {}

    # 1️⃣ محاولة جلب الموديولات من السجل المركزي للداشبورد إن وجد
    try:
        from apps.suppliers_dashboard.registry import MODULES_REGISTRY
        if MODULES_REGISTRY:
            supplier_modules.update(MODULES_REGISTRY)
    except ImportError:
        pass

    # 2️⃣ محاولة جلب الموديولات الممررة على مستوى التطبيق (current_app)
    if hasattr(current_app, 'supplier_modules') and current_app.supplier_modules:
        supplier_modules.update(current_app.supplier_modules)

    # 3️⃣ المسح الديناميكي على كافة سجلات الموديولات (Registries) المسجلة في التطبيق
    registry_paths = [
        'apps.supplier_products.registry',
        'apps.supplier_orders.registry',
        'apps.supplier_wallet.registry',
        'apps.suppliers_dashboard.registry'
    ]

    for path in registry_paths:
        try:
            mod = importlib.import_module(path)
            if hasattr(mod, 'get_nav_metadata'):
                metadata = mod.get_nav_metadata()
                if metadata.get('show_in_supplier', True):
                    supplier_modules[metadata['key']] = metadata
            elif hasattr(mod, 'MODULES_REGISTRY') and isinstance(mod.MODULES_REGISTRY, dict):
                supplier_modules.update(mod.MODULES_REGISTRY)
        except (ImportError, AttributeError):
            continue

    # 4️⃣ في حالة التعذر الكامل، يتم تقديم الموديول الحالي كقيمة احتياطية بدلاً من تقييد القائمة
    if not supplier_modules:
        supplier_modules['supplier_wallet'] = {
            'title': 'المحفظة الرقمية',
            'icon': 'fas fa-wallet',
            'links': {
                'supplier_wallet_bp.transactions_redirect': 'حركة المحفظة',
                'supplier_wallet_bp.withdraw_redirect': 'سحب الرصيد'
            }
        }

    return supplier_modules


def get_current_wallet_identifier():
    """الحصول على المعرف الخاص بالمحفظة."""
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


# --- مسارات إعادة التوجيه السريعة ---

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
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))


# --- مسارات اللوحة والصفحات المالية ---

@supplier_wallet_bp.route('/<string:wallet_id>/', strict_slashes=False)
@supplier_wallet_bp.route('/<string:wallet_id>/dashboard', strict_slashes=False)
@login_required
def wallet_dashboard(wallet_id):
    """إعادة توجيه تلقائية من مسار dashboard إلى سجل المعاملات."""
    return redirect(url_for('supplier_wallet_bp.transactions', wallet_id=wallet_id))


@supplier_wallet_bp.route('/<string:wallet_id>/transactions', strict_slashes=False)
@login_required
def transactions(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        return safe_redirect_home()

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet:
        try:
            wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Transactions Wallet Error]: {str(e)}")
            traceback.print_exc()
            return safe_redirect_home()

    # ✅ جلب الحركات بالترتيب الزمني (من الأقدم للأحدث)
    transactions_list = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.asc()).all()
    all_transactions = list(transactions_list)

    # ✅ إضافة الرصيد بعد كل حركة (balance_after) - حساب تراكمي للخلف
    running_balance = Decimal(str(wallet.balance))  # نبدأ من الرصيد الحالي
    for trx in reversed(all_transactions):
        trx.balance_after = running_balance
        if trx.transaction_type in ['credit', 'deposit']:
            running_balance = running_balance - Decimal(str(trx.amount))
        elif trx.transaction_type in ['debit', 'withdraw']:
            running_balance = running_balance + Decimal(str(trx.amount))

    # ✅ ترتيبهم من الأحدث للأقدم للعرض
    all_transactions.reverse()

    def get_sort_key(t):
        dt = getattr(t, 'created_at', None)
        return dt if dt is not None else datetime.min

    all_transactions.sort(key=get_sort_key, reverse=True)

    search_query = request.args.get('q', '').strip()
    trans_type = request.args.get('trans_type', '').strip()
    status = request.args.get('status', '').strip()

    if search_query:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                v_num = str(t.get('voucher_number', '') or '')
                r_num = str(t.get('reference_number', '') or '')
            else:
                v_num = str(getattr(t, 'voucher_number', '') or '')
                r_num = str(getattr(t, 'reference_number', '') or '')
            if search_query.lower() in v_num.lower() or search_query.lower() in r_num.lower():
                filtered_list.append(t)
        all_transactions = filtered_list

    if trans_type:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                t_type = t.get('transaction_type')
            else:
                t_type = getattr(t, 'transaction_type', None)
                if hasattr(t_type, 'value'):
                    t_type = t_type.value
            if str(t_type).lower() == trans_type.lower():
                filtered_list.append(t)
        all_transactions = filtered_list

    if status:
        filtered_list = []
        for t in all_transactions:
            if isinstance(t, dict):
                s_val = t.get('status')
            else:
                s_val = getattr(t, 'status', None)
                if hasattr(s_val, 'value'):
                    s_val = s_val.value
            if str(s_val).lower() == status.lower():
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
        get_trx_type_attr=get_trx_type_attr,
        now=datetime.now()
    )


@supplier_wallet_bp.route('/<string:wallet_id>/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw(wallet_id):
    supplier_id = get_current_supplier_id()
    if not supplier_id and hasattr(current_user, 'id'):
        supplier_id = current_user.id

    if not supplier_id:
        return safe_redirect_home()

    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    if not wallet and hasattr(SupplierWallet, 'wallet_code'):
        wallet = SupplierWallet.query.filter_by(wallet_code=wallet_id).first()

    if not wallet:
        try:
            wallet = WalletService.get_or_create_wallet(db.session, supplier_id, getattr(current_user, 'trade_name', 'متجر المورد'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [Withdrawal Get/Create Wallet Error]: {str(e)}")
            traceback.print_exc()
            return safe_redirect_home()

    current_balance = get_wallet_balance(wallet)

    if request.method == 'POST':
        try:
            # 🛑 1. التحقق من عدم وجود طلب سحب معلق آخر للمحفظة
            has_pending = WithdrawalRequest.query.filter_by(wallet_id=wallet.id, status='pending').first()
            if has_pending:
                raise ValueError("لديك طلب سحب قيد المراجعة حالياً، لا يمكنك تقديم طلب جديد حتى يتم البت فيه.")

            raw_amount = request.form.get('amount', '0').strip().replace(',', '.')
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')

            # 🛑 2. تطبيق شرط إبقاء 50 ريال احتياطي في المحفظة
            reserved_balance = Decimal('50.00')
            available_balance = current_balance - reserved_balance
            if available_balance < Decimal('0.00'):
                available_balance = Decimal('0.00')

            min_withdrawal = Decimal('10.00')
            if amount < min_withdrawal:
                raise ValueError(f"أدنى مبلغ يمكن سحبه هو {min_withdrawal:.2f} ر.س")

            if amount > available_balance:
                raise ValueError(
                    f"لا يمكنك سحب هذا المبلغ. يجب الإبقاء على {reserved_balance:.2f} ر.س كحد أدنى في المحفظة. "
                    f"المبلغ المتاح لك للسحب حالياً هو {available_balance:.2f} ر.س فقط."
                )

            bank_account = request.form.get('bank_account_id', 'الحساب البنكي المعتمد للمورد')
            notes = request.form.get('notes', '')

            wdr = WalletService.create_withdrawal_request(db.session, wallet.id, bank_account, amount, notes)
            db.session.commit()

            NotificationService.notify_withdrawal_requested(float(amount), wdr.request_number)
            flash("تم تقديم طلب السحب بنجاح، وهو قيد المراجعة والتدقيق حالياً.", "success")
            return redirect(url_for('supplier_wallet_bp.withdraw', wallet_id=wallet_id, success='true'))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
            print(f"⚠️ [Withdrawal ValueError]: {str(e)}")
            NotificationService.notify_error(str(e), "خطأ في طلب السحب")
        except Exception as e:
            db.session.rollback()
            flash("حدث خطأ غير متوقع أثناء معالجة طلب السحب، يرجى المحاولة لاحقاً.", "danger")
            print(f"⚠️ [Withdrawal Exception]: {str(e)}")
            traceback.print_exc()
            NotificationService.notify_error(f"حدث خطأ غير متوقع: {str(e)}", "خطأ نظام")

        return redirect(url_for('supplier_wallet_bp.withdraw', wallet_id=wallet_id))

    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '').strip()
        status_filter = request.args.get('status', '').strip()

        query = WithdrawalRequest.query.filter_by(wallet_id=wallet.id)

        if search_query:
            query = query.filter(WithdrawalRequest.request_number.ilike(f"%{search_query}%"))

        if status_filter:
            if status_filter == 'approved':
                query = query.filter(WithdrawalRequest.status.in_(['approved', 'completed']))
            else:
                query = query.filter(WithdrawalRequest.status == status_filter)

        query = query.order_by(WithdrawalRequest.created_at.desc())

        pagination = query.paginate(page=page, per_page=10, error_out=False)
        latest_request = query.first()

        active_bank = {
            'bank_name': 'الحساب البنكي المعتمد للمورد',
            'id': 1
        }
        modules = get_sidebar_modules()

        return render_template(
            'supplier_wallet/withdrawal_form.html',
            wallet=wallet,
            balance=current_balance,
            active_bank=active_bank,
            pagination=pagination,
            latest_request=latest_request,
            supplier_modules=modules,
            modules_registry=modules
        )
    except Exception as e:
        print(f"⚠️ [Withdraw Render Error]: {str(e)}")
        traceback.print_exc()
        return safe_redirect_home()


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
    modules = get_sidebar_modules()

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
        transaction=transaction,  # ✅ تمرير الحركة المالية الصحيحة
        supplier_modules=modules,
        modules_registry=modules
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
