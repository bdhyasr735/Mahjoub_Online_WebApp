# -*- coding: utf-8 -*-
"""
Mahjoub Online - Supplier Wallet Routes
تتضمن كافة المنطق للفلترة ومعالجة حركات الحساب وطلبات السحب مباشرة
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for

wallet_bp = Blueprint(
    'wallet', 
    __name__, 
    template_folder='templates', 
    static_folder='static'
)

class CustomPagination:
    """فئة محاكاة لكائنات الترقيم لتدعم القالب بشكل كامل"""
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page)
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=1, right_edge=1, left_current=2, right_current=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def apply_wallet_filters_logic(transactions, args):
    search_query = args.get('search', '').strip().lower()
    trx_type = args.get('type', 'all')
    status = args.get('status', 'all')
    start_date = args.get('start_date', '')
    end_date = args.get('end_date', '')

    filtered = []
    for trx in transactions:
        if trx_type != 'all' and trx.get('trx_type') != trx_type:
            continue
        if status != 'all' and trx.get('status') != status:
            continue
        if search_query:
            ref = str(trx.get('reference_code', '')).lower()
            desc = str(trx.get('description', '')).lower()
            prod = str(trx.get('product_name', '')).lower()
            if search_query not in ref and search_query not in desc and search_query not in prod:
                continue
        if start_date and trx.get('created_at', '') < start_date:
            continue
        if end_date and trx.get('created_at', '') > end_date:
            continue
        filtered.append(trx)
    return filtered


@wallet_bp.route('/wallet', methods=['GET'])
def wallet():
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    summary = {
        'total_balance': 48500.00,
        'available_balance': 35200.00,
        'pending_balance': 8300.00,
        'total_withdrawn': 24000.00,
        'currency': 'ج.م'
    }

    mock_transactions = [
        {
            'id': 1,
            'reference_code': 'TRX-98412',
            'created_at': '2026-08-10 14:20',
            'trx_type': 'credit',
            'description': 'أرباح مبيعات طلبية #ORD-7712',
            'amount': 4500.00,
            'status': 'completed',
            'product_name': 'طقم أدوات صحية فاخر',
            'quantity': 3,
            'unit_price': 1500.00
        },
        {
            'id': 2,
            'reference_code': 'TRX-98413',
            'created_at': '2026-08-09 11:15',
            'trx_type': 'debit',
            'description': 'طلب سحب رصيد إلى فودافون كاش #WDR-104',
            'amount': 2500.00,
            'status': 'completed'
        },
        {
            'id': 3,
            'reference_code': 'TRX-98414',
            'created_at': '2026-08-08 09:45',
            'trx_type': 'credit',
            'description': 'أرباح توريد خلاطات مياه #ORD-7688',
            'amount': 8300.00,
            'status': 'pending',
            'product_name': 'خلاط مياه إيطالي',
            'quantity': 5,
            'unit_price': 1660.00
        }
    ]

    filtered_list = apply_wallet_filters_logic(mock_transactions, request.args)
    total_items = len(filtered_list)
    current_page = max(1, min(page, max(1, (total_items + PER_PAGE - 1) // PER_PAGE)))
    start_idx = (current_page - 1) * PER_PAGE
    paginated_items = filtered_list[start_idx:start_idx + PER_PAGE]

    # استخدام الفئة الجديدة بدلاً من القاموس لتجنب أخطاء القالب
    pagination = CustomPagination(paginated_items, current_page, PER_PAGE, total_items)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        pagination=pagination
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    summary = {
        'available_balance': 35200.00,
        'min_withdraw_amount': 500.00,
        'currency': 'ج.م'
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank_transfer')
            account_details = request.form.get('account_details', '')

            if amount < summary['min_withdraw_amount']:
                flash(f"الحد الأدنى للسحب هو {summary['min_withdraw_amount']} ج.م", "danger")
            elif amount > summary['available_balance']:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح للسحب!", "danger")
            elif not account_details.strip():
                flash("يرجى إدخال تفاصيل الحساب أو رقم المحفظة بشكل صحيح.", "danger")
            else:
                flash("تم تقديم طلب السحب بنجاح وهو قيد المعالجة والتسوية.", "success")
                return redirect(url_for('wallet.withdraw'))
        except ValueError:
            flash("يرجى إدخال قيمة مالية صحيحة.", "danger")

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    mock_withdrawals = [
        {
            'id': 101,
            'reference_code': 'WDR-104',
            'created_at': '2026-08-09 11:15',
            'amount': 2500.00,
            'method': 'vodafone_cash',
            'account_details': '01012345678',
            'status': 'approved'
        },
        {
            'id': 102,
            'reference_code': 'WDR-105',
            'created_at': '2026-08-11 16:30',
            'amount': 5000.00,
            'method': 'bank_transfer',
            'account_details': 'البنك الأهلي - IBAN EG0123456789',
            'status': 'pending'
        }
    ]

    total_items = len(mock_withdrawals)
    current_page = max(1, min(page, max(1, (total_items + PER_PAGE - 1) // PER_PAGE)))
    start_idx = (current_page - 1) * PER_PAGE
    paginated_withdrawals = mock_withdrawals[start_idx:start_idx + PER_PAGE]

    pagination = CustomPagination(paginated_withdrawals, current_page, PER_PAGE, total_items)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        pagination=pagination
    )
