# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id,
    get_or_create_supplier_wallet,
    get_registered_supplier_payout_info
)

# الحد الأدنى المسموح به لتقديم طلب سحب
MIN_WITHDRAW_AMOUNT = Decimal('50.00')


@supplier_wallet_bp.route('/', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/wallet', methods=['GET'], strict_slashes=False)
@login_required
def wallet_dashboard():
    """عرض لوحة المحفظة العامة وكشف حساب المعاملات المالية للمورد."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    # حساب الملخص المالي والأرصدة
    balance_sar = float(getattr(wallet_obj, 'balance_sar', 0.00)) if wallet_obj else 0.00
    balance_pending = float(getattr(wallet_obj, 'balance_pending', 0.00)) if wallet_obj else 0.00
    total_withdrawn = float(getattr(wallet_obj, 'total_withdrawn', 0.00)) if wallet_obj else 0.00
    curr = getattr(wallet_obj, 'default_currency', 'SAR') if wallet_obj else 'SAR'

    summary = {
        'balance_sar': balance_sar,
        'available_balance': balance_sar,
        'balance_pending': balance_pending,
        'total_withdrawn': total_withdrawn,
        'currency': curr,
        'min_withdraw_amount': float(MIN_WITHDRAW_AMOUNT)
    }

    # معاملات الفلترة، البحث، والتقسيم (Pagination)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    search_query = request.args.get('q', '').strip()

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    if type_filter != 'all':
        query = query.filter(WalletTransaction.trans_type == type_filter)

    if search_query:
        query = query.filter(
            db.or_(
                WalletTransaction.reference_number.ilike(f"%{search_query}%"),
                WalletTransaction.voucher_number.ilike(f"%{search_query}%"),
                WalletTransaction.description.ilike(f"%{search_query}%")
            )
        )

    # الترتيب تنازلياً حسب التاريخ والرقم المعرف
    pagination_obj = query.order_by(
        WalletTransaction.created_at.desc(), 
        WalletTransaction.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'supplier_wallet/wallet.html',
        wallet=wallet_obj,
        summary=summary,
        transactions=pagination_obj.items,
        pagination=pagination_obj,
        active_status=status_filter,
        active_type=type_filter,
        search_query=search_query,
        registered_owner=registered_owner,
        registered_details=registered_details
    )


@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    """عرض صفحة طلبات السحب ومعالجة تقديم طلب سحب رصيد جديد."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    if not wallet_obj:
        flash('لم يتم العثور على محفظة المورد.', 'danger')
        return redirect(url_for('supplier_wallet.wallet_dashboard'))

    balance_sar = float(getattr(wallet_obj, 'balance_sar', 0.00))
    curr = getattr(wallet_obj, 'default_currency', 'SAR')

    summary = {
        'available_balance': balance_sar,
        'balance_sar': balance_sar,
        'min_withdraw_amount': float(MIN_WITHDRAW_AMOUNT),
        'currency': curr
    }

    # معالجة طلب السحب المالي عند إرسال النموذج (POST)
    if request.method == 'POST':
        try:
            amount_raw = request.form.get('amount', '0').strip()
            amount = Decimal(amount_raw)
        except (ValueError, TypeError, InvalidOperation):
            flash('يرجى إدخال مبلغ سحب صحيح.', 'danger')
            return redirect(url_for('supplier_wallet.withdraw'))

        if amount < MIN_WITHDRAW_AMOUNT:
            flash(f'الحد الأدنى لطلب السحب هو {MIN_WITHDRAW_AMOUNT} {curr}.', 'danger')
            return redirect(url_for('supplier_wallet.withdraw'))

        available_decimal = Decimal(str(wallet_obj.balance_sar or 0))
        if amount > available_decimal:
            flash('رصيد المحفظة الحالي غير كافٍ لإتمام عملية السحب.', 'danger')
            return redirect(url_for('supplier_wallet.withdraw'))

        payout_method = request.form.get('method', 'bank')
        method_label = 'تحويل بنكي' if payout_method == 'bank' else 'شركات التحويل والصرافة'
        full_description = f'طلب سحب مالي | طريقة التحويل: {method_label}'

        try:
            # إنشاء معاملة سحب معلقة
            transaction = WalletTransaction(
                wallet_id=wallet_obj.id,
                owner_type='supplier',
                owner_id=supplier_id,
                trans_type='withdrawal',
                status='pending',
                amount=amount,
                currency=curr,
                description=full_description
            )

            db.session.add(transaction)
            db.session.commit()

            ref_num = getattr(transaction, 'reference_number', None) or f"#{transaction.id}"
            flash(f'تم إرسال طلب السحب بنجاح برقم مرجعي: {ref_num}', 'success')
            return redirect(url_for('supplier_wallet.withdraw'))

        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ غير متوقع أثناء معالجة طلب السحب: {str(e)}', 'danger')
            return redirect(url_for('supplier_wallet.withdraw'))

    # عرض سجل طلبات السحب (GET)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status', 'all')

    query = WalletTransaction.query.filter_by(
        wallet_id=wallet_obj.id,
        trans_type='withdrawal'
    )

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(
        WalletTransaction.created_at.desc(),
        WalletTransaction.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'supplier_wallet/withdraw.html',
        wallet=wallet_obj,
        summary=summary,
        pagination=pagination_obj
    )


@supplier_wallet_bp.route('/export-pdf', methods=['GET'], strict_slashes=False)
@login_required
def export_wallet_pdf():
    """تصدير كشف حساب المحفظة كملف PDF."""
    flash('جاري إعداد تقرير كشف الحساب بصيغة PDF...', 'info')
    return redirect(url_for('supplier_wallet.wallet_dashboard'))
