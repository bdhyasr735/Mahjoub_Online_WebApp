# coding: utf-8
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from apps.supplier_wallet.services import WalletService
from apps.models.wallet_db import SupplierWallet, WalletTransaction # تأكد من استيراد الموديلات
from datetime import datetime, timedelta

supplier_wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates')

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # 1. جلب المحفظة
    wallet = getattr(current_user, 'wallet', None) or WalletService.get_supplier_wallet(current_user.id)
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة مرتبطة بحسابك.")

    # 2. الفلترة
    all_transactions = wallet.transactions
    
    currency = request.args.get('currency')
    if currency:
        all_transactions = [t for t in all_transactions if t.currency == currency]

    search = request.args.get('search', '').lower().strip()
    if search:
        all_transactions = [
            t for t in all_transactions 
            if search in str(t.voucher_number or "").lower() or 
               search in (t.description or "").lower()
        ]

    filter_type = request.args.get('filter_type', 'all')
    now = datetime.now()
    if filter_type == 'day':
        all_transactions = [t for t in all_transactions if t.created_at.date() == now.date()]
    elif filter_type == 'week':
        all_transactions = [t for t in all_transactions if t.created_at >= (now - timedelta(days=7))]
    elif filter_type == 'month':
        all_transactions = [t for t in all_transactions if t.created_at.month == now.month and t.created_at.year == now.year]

    all_transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    # 3. الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    offset = (page - 1) * per_page
    transactions_paginated = all_transactions[offset : offset + per_page]
    
    pagination = Pagination(
        page=page, total=len(all_transactions), per_page=per_page,
        css_framework='bootstrap5', record_name='حركة',
        # هام: الحفاظ على الفلاتر في روابط الصفحات
        href=f'?currency={currency or ""}&filter_type={filter_type}&search={search}'
    )

    total_debit = sum(t.amount for t in all_transactions if t.trans_type == 'debit')
    total_credit = sum(t.amount for t in all_transactions if t.trans_type == 'credit')

    # AJAX Response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('supplier_wallet/_table_partial.html', transactions=transactions_paginated)

    return render_template(
        'supplier_wallet/supplier_wallet.html', 
        wallet=wallet,
        transactions=transactions_paginated, 
        pagination=pagination,
        total_debit=total_debit,
        total_credit=total_credit,
        now=now 
    )
