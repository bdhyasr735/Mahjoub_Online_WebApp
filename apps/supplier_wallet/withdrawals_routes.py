# -*- coding: utf-8 -*-
# 📂 apps/supplier_wallet/withdrawals_routes.py

from decimal import Decimal

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WithdrawalRequest
from apps.supplier_wallet.routes import supplier_wallet_bp, get_current_supplier_id, get_wallet_balance, get_sidebar_modules, safe_redirect_home
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService


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
            return safe_redirect_home()

    current_balance = get_wallet_balance(wallet)
    
    # ✅ حساب المتغيرات وإضافة المتغيرات الناقصة التي يحتاجها القالب
    reserved_balance = Decimal('50.00')
    available_balance = current_balance - reserved_balance
    if available_balance < Decimal('0.00'):
        available_balance = Decimal('0.00')
    
    min_withdrawal_amount = Decimal('10.00')
    currency_symbol = getattr(wallet, 'currency', 'ر.س')

    if request.method == 'POST':
        try:
            has_pending = WithdrawalRequest.query.filter_by(wallet_id=wallet.id, status='pending').first()
            if has_pending:
                raise ValueError("لديك طلب سحب قيد المراجعة حالياً، لا يمكنك تقديم طلب جديد حتى يتم البت فيه.")

            raw_amount = request.form.get('amount', '0').strip().replace(',', '.')
            amount = Decimal(raw_amount) if raw_amount else Decimal('0')

            if amount < min_withdrawal_amount:
                raise ValueError(f"أدنى مبلغ يمكن سحبه هو {min_withdrawal_amount:.2f} {currency_symbol}")

            if amount > available_balance:
                raise ValueError(
                    f"لا يمكنك سحب هذا المبلغ. يجب الإبقاء على {reserved_balance:.2f} {currency_symbol} كحد أدنى في المحفظة. "
                    f"المبلغ المتاح لك للسحب حالياً هو {available_balance:.2f} {currency_symbol} فقط."
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
            NotificationService.notify_error(str(e), "خطأ في طلب السحب")
        except Exception as e:
            db.session.rollback()
            flash("حدث خطأ غير متوقع أثناء معالجة طلب السحب، يرجى المحاولة لاحقاً.", "danger")

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

        active_bank = {'bank_name': 'الحساب البنكي المعتمد للمورد', 'id': 1}
        
        modules = get_sidebar_modules()
        
        if not modules or 'supplier_wallet' not in modules:
            modules['supplier_wallet'] = {
                'title': 'المحفظة الرقمية',
                'icon': 'fas fa-wallet',
                'links': {
                    'supplier_wallet_bp.transactions_redirect': 'حركة المحفظة',
                    'supplier_wallet_bp.withdraw_redirect': 'سحب الرصيد'
                }
            }

        return render_template(
            'supplier_wallet/withdrawal_form.html',
            wallet=wallet,
            balance=current_balance,
            available_balance=available_balance,  # ✅ إضافة المتغير
            min_withdrawal_amount=min_withdrawal_amount,  # ✅ إضافة المتغير
            currency_symbol=currency_symbol,  # ✅ إضافة رمز العملة
            active_bank=active_bank,
            pagination=pagination,
            latest_request=latest_request,
            supplier_modules=modules,
            modules_registry=modules
        )
    except Exception as e:
        print(f"❌ [Withdraw Error]: {e}")
        return safe_redirect_home()
