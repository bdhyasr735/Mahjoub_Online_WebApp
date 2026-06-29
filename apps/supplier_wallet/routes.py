# coding: utf-8
from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from apps.supplier_wallet.services import WalletService
from datetime import datetime, timedelta

supplier_wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__, 
    template_folder='templates'
)

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # 1. جلب المحفظة
    wallet = getattr(current_user, 'wallet', None) or WalletService.get_supplier_wallet(current_user.id)
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة مرتبطة بحسابك.")

    # 2. تطبيق الفلاتر
    all_transactions = wallet.transactions
    
    # أ. فلتر العملة
    currency_filter = request.args.get('currency')
    if currency_filter:
        all_transactions = [t for t in all_transactions if t.currency == currency_filter]

    # ب. فلتر البحث اللحظي (مرن: يبحث في رقم السند أو البيان)
    search_query = request.args.get('search', '').lower().strip()
    if search_query:
        all_transactions = [
            t for t in all_transactions 
            if search_query in str(t.voucher_number).lower() or 
               search_query in (t.description or "").lower()
        ]

    # ج. فلتر الزمن
    filter_type = request.args.get('filter_type', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    now = datetime.now()

    if filter_type == 'day':
        all_transactions = [t for t in all_transactions if t.created_at.date() == now.date()]
    elif filter_type == 'week':
        all_transactions = [t for t in all_transactions if t.created_at >= (now - timedelta(days=7))]
    elif filter_type == 'month':
        all_transactions = [t for t in all_transactions if t.created_at.month == now.month and t.created_at.year == now.year]
    elif start_date and end_date:
        try:
            s = datetime.strptime(start_date, '%Y-%m-%d')
            e = datetime.strptime(end_date, '%Y-%m-%d')
            all_transactions = [t for t in all_transactions if s.date() <= t.created_at.date() <= e.date()]
        except ValueError:
            pass

    # الترتيب حسب الأحدث
    all_transactions = sorted(all_transactions, key=lambda x: x.created_at, reverse=True)
    
    # 3. إعداد الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    offset = (page - 1) * per_page
    transactions_paginated = all_transactions[offset : offset + per_page]
    
    pagination = Pagination(
        page=page, 
        total=len(all_transactions), 
        per_page=per_page, 
        css_framework='bootstrap5',
        record_name='حركة'
    )

    # 4. حساب الإجماليات (على النتائج المفلترة فقط)
    total_debit = sum(t.amount for t in all_transactions if t.trans_type == 'debit')
    total_credit = sum(t.amount for t in all_transactions if t.trans_type == 'credit')

    # استجابة AJAX للبحث اللحظي
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('supplier_wallet/_table_partial.html', transactions=transactions_paginated)

    # العرض العادي
    return render_template(
        'supplier_wallet/supplier_wallet.html', 
        wallet=wallet,
        transactions=transactions_paginated, 
        pagination=pagination,
        total_debit=total_debit,
        total_credit=total_credit,
        now=now 
    )
