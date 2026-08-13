# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from decimal import Decimal
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
    """عرض كشف الحساب المحاسبي الفعلي للمورد (الحركات المكتملة فقط)."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    # الأرصدة والملخص المالي
    balance_sar = float(getattr(wallet_obj, 'balance_sar', 0.00)) if wallet_obj else 0.00
    total_withdrawn = float(getattr(wallet_obj, 'total_withdrawn', 0.00)) if wallet_obj else 0.00
    curr = getattr(wallet_obj, 'default_currency', 'SAR') if wallet_obj else 'SAR'

    summary = {
        'balance_sar': balance_sar,
        'available_balance': balance_sar,
        'total_withdrawn': total_withdrawn,
        'currency': curr
    }

    # الفلترة والتقسيم (Pagination)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    type_filter = request.args.get('type', 'all')
    search_query = request.args.get('q', '').strip()

    # 🛑 جلب الحركات المكتملة فقط (Completed) لضمان صحة كشف الحساب المحاسبي
    query = WalletTransaction.query.filter_by(
        wallet_id=wallet_obj.id if wallet_obj else -1,
        status='completed'
    )

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
        active_type=type_filter,
        search_query=search_query,
        registered_owner=registered_owner,
        registered_details=registered_details
    )
