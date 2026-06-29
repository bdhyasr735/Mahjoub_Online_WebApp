# 📂 apps/supplier_wallet/routes.py
from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from datetime import datetime

supplier_wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates')

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # جلب المحفظة
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة.")

    # الاستعلام الأساسي من قاعدة البيانات مباشرة
    query = WalletTransaction.query.filter_by(wallet_id=wallet.id)

    # 1. فلتر العملة
    currency = request.args.get('currency')
    if currency:
        query = query.filter_by(currency=currency)

    # 2. البحث المرن (في البيان أو رقم السند)
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (WalletTransaction.voucher_number.ilike(f'%{search}%')) | 
            (WalletTransaction.description.ilike(f'%{search}%'))
        )

    # ترتيب النتائج
    all_transactions = query.order_by(WalletTransaction.created_at.desc()).all()
    
    # الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    offset = (page - 1) * per_page
    transactions_paginated = all_transactions[offset : offset + per_page]
    
    pagination = Pagination(page=page, total=len(all_transactions), per_page=per_page, css_framework='bootstrap5')

    # حساب الإجماليات
    total_debit = sum(t.amount for t in all_transactions if t.trans_type == 'debit')
    total_credit = sum(t.amount for t in all_transactions if t.trans_type == 'credit')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('supplier_wallet/_table_partial.html', transactions=transactions_paginated)

    return render_template(
        'supplier_wallet/supplier_wallet.html', 
        wallet=wallet,
        transactions=transactions_paginated, 
        pagination=pagination,
        total_debit=total_debit,
        total_credit=total_credit,
        now=datetime.utcnow()
    )
