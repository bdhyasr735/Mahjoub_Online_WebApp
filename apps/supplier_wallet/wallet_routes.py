# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id,
    get_or_create_supplier_wallet,
    get_registered_supplier_payout_info
)

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
        'balance_pending': balance_pending,
        'total_withdrawn': total_withdrawn,
        'currency': curr
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

    pagination_obj = query.order_by(WalletTransaction.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

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
