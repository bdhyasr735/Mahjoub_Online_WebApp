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

    # ربط ملخص الحساب من قاعدة البيانات الفعلية (Models)
    summary = {
        'total_balance': 0.00,
        'available_balance': 0.00,
        'pending_balance': 0.00,
        'total_withdrawn': 0.00,
        'currency': 'ر.ي'
    }

    transactions = [] # يتم جلب المعاملات الحقيقية من قاعدة البيانات هنا

    filtered_list = apply_wallet_filters_logic(transactions, request.args)
    total_items = len(filtered_list)
    current_page = max(1, min(page, max(1, (total_items + PER_PAGE - 1) // PER_PAGE)))
    start_idx = (current_page - 1) * PER_PAGE
    paginated_items = filtered_list[start_idx:start_idx + PER_PAGE]

    pagination = CustomPagination(paginated_items, current_page, PER_PAGE, total_items)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        pagination=pagination
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    # جلب رصيد المورد الحقيقي والحد الأدنى المسموح به من قاعدة البيانات أو الإعدادات
    summary = {
        'available_balance': 0.00,
        'min_withdraw_amount': 0.00,
        'currency': 'ر.ي'
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank_transfer')
            account_details = request.form.get('account_details', '')

            if amount < summary['min_withdraw_amount']:
                flash(f"الحد الأدنى للسحب هو {summary['min_withdraw_amount']} {summary['currency']}", "danger")
            elif amount > summary['available_balance']:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح للسحب!", "danger")
            elif not account_details.strip():
                flash("يرجى إدخال تفاصيل الحساب أو رقم المحفظة بشكل صحيح.", "danger")
            else:
                # كتابة منطق حفظ طلب السحب الحقيقي في قاعدة البيانات هنا
                flash("تم تقديم طلب السحب بنجاح وهو قيد المعالجة والتسوية.", "success")
                return redirect(url_for('wallet.withdraw'))
        except ValueError:
            flash("يرجى إدخال قيمة مالية صحيحة.", "danger")

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    withdrawals = [] # يتم جلب طلبات السحب الحقيقية من قاعدة البيانات هنا

    total_items = len(withdrawals)
    current_page = max(1, min(page, max(1, (total_items + PER_PAGE - 1) // PER_PAGE)))
    start_idx = (current_page - 1) * PER_PAGE
    paginated_withdrawals = withdrawals[start_idx:start_idx + PER_PAGE]

    pagination = CustomPagination(paginated_withdrawals, current_page, PER_PAGE, total_items)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        pagination=pagination
    )
