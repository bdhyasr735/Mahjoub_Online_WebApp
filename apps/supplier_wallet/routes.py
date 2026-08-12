# -*- coding: utf-8 -*-
"""
مسارات محفظة المورد (Wallet Routes)
الفصل التام بين مسار المحفظة (/wallet) لكشف الحساب العام، ومسار السحب (/withdraw) لطلبات السحب.
Mahjoub Online WebApp - supplier_wallet/routes.py
"""

import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app

from .registry import wallet_bp
from .components.filters import WalletFilterComponent
from .components.tables import WalletTableComponent

# ملاحظة: استيراد الموديلات وقاعدة البيانات من الموديول أو التطبيق الرئيسي
# from apps.supplier_wallet.models import SupplierWallet, WalletTransaction, WithdrawalRequest
# from apps import db

@wallet_bp.route('/wallet', methods=['GET'])
def wallet_statement():
    """
    مسار كشف الحساب العام للمحفظة (/supplier/wallet)
    يعرض ملخص الرصيد، حركات المحفظة، الفلاتر، مع الترقيم (10 حركات لكل صفحة).
    """
    # 1. استلام رقم الصفحة من رابط الطلب (الافتراضي 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # إجبار الترقيم على 10 عناصر فقط في كل صفحة لتحسين الأداء

    # 2. تحديد هية المورد المسجل (مثال: المورد الحالي المفترض)
    # current_supplier_id = current_user.supplier_id

    # 3. جلب بيانات كشف حساب المحفظة الحالي أو استخدام قيم افتراضية
    # wallet = SupplierWallet.query.filter_by(supplier_id=current_supplier_id).first()
    
    # ملخص الحساب
    summary = {
        'total_balance': 48500.00,
        'available_balance': 35200.00,
        'pending_balance': 8300.00,
        'total_withdrawn': 24000.00,
        'currency': 'ج.م'
    }

    # 4. تجهيز كويري المعاملات مع تطبيق الفلاتر عبر components/filters.py
    # base_query = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(WalletTransaction.created_at.desc())
    # query_filtered, applied_filters = WalletFilterComponent.apply_transaction_filters(
    #     base_query, request.args, WalletTransaction
    # )

    # 5. تطبيق خاصية الترقيم per_page=10 عبر paginate() من Flask-SQLAlchemy
    # transactions_pagination = query_filtered.paginate(
    #     page=page,
    #     per_page=per_page,
    #     error_out=False
    # )

    # لتسهيل تشغيل الكود وفحصه بصورة مستقلة بدون DB فعلية، نمرر بيانات وهمية منسقة بدقة:
    # (في التطبيق الفعلي يستبدل الكائن بالتالي: transactions_pagination)
    applied_filters = {
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'type': request.args.get('type', 'all'),
        'status': request.args.get('status', 'all'),
        'search': request.args.get('search', '')
    }

    # محاكاة قائمة الترقيم 10 حركات لكل صفحة
    all_mock_transactions = _generate_mock_transactions()
    
    # فلترة الحركات وهمياً للتجربة
    filtered_trxs = [
        t for t in all_mock_transactions
        if (applied_filters['type'] == 'all' or t['trx_type'] == applied_filters['type']) and
           (applied_filters['status'] == 'all' or t['status'] == applied_filters['status'])
    ]

    total_items = len(filtered_trxs)
    total_pages = (total_items + per_page - 1) // per_page or 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = filtered_trxs[start_idx:end_idx]

    # كائن الترقيم المشابه لكائن Flask-SQLAlchemy Pagination
    class MockPagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1
            self.next_num = page + 1

        def iter_pages(self, left_edge=1, left_current=2, right_current=2, right_edge=1):
            for i in range(1, self.pages + 1):
                yield i

    pagination = MockPagination(page_items, page, per_page, total_items, total_pages)

    # 6. تنسيق الصفوف باستخدام components/tables.py
    formatted_rows = [
        WalletTableComponent.format_transaction_row(_DictToObj(t))
        for t in pagination.items
    ]

    filter_options = {
        'type_options': WalletFilterComponent.get_type_options(),
        'status_options': WalletFilterComponent.get_status_options()
    }

    return render_template(
        'supplier_wallet/wallet.html',  # تم التصحيح ليطابق اسم الملف wallet.html
        summary=summary,
        pagination=pagination,
        transactions=formatted_rows,
        applied_filters=applied_filters,
        filter_options=filter_options
    )


@wallet_bp.route('/withdraw', methods=['GET', 'POST'])
def withdraw_request():
    """
    مسار سحب الرصيد المستقل (/supplier/withdraw)
    صفحة مستقلة لإنشاء طلبات سحب رصيد جديدة ومتابعة سجل الطلبات السابقة مع الترقيم.
    """
    # 1. استلام رقم الصفحة للسجل التاريجي لطلبات السحب
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 10 طلبات سحب لكل صفحة

    summary = {
        'available_balance': 35200.00,
        'min_withdraw_amount': 500.00,
        'currency': 'ج.م'
    }

    # 2. معالجة نموذج طلب سحب رصيد جديد (POST Method)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', '').strip()
            account_details = request.form.get('account_details', '').strip()
            notes = request.form.get('notes', '').strip()

            # التحقق من المدخلات
            if amount < summary['min_withdraw_amount']:
                flash(f"الحد الأدنى لمبلغ السحب هو {summary['min_withdraw_amount']} {summary['currency']}", "error")
            elif amount > summary['available_balance']:
                flash("المبلغ المطلوب أكبر من الرصيد المتاح للسحب في محفظتك!", "error")
            elif not method or not account_details:
                flash("يرجى اختيار طريقة السحب وإدخال تفاصيل الحساب بشكل صحيح.", "error")
            else:
                # إنشاء رمز كود للطلب جديد
                request_code = f"WD-{uuid.uuid4().hex[:8].upper()}"

                # حفظ الطلب في قاعدة البيانات (في الكود الفعلي)
                # new_request = WithdrawalRequest(
                #     wallet_id=wallet.id,
                #     request_code=request_code,
                #     amount=amount,
                #     method=method,
                #     account_details=account_details,
                #     notes=notes,
                #     status='pending'
                # )
                # db.session.add(new_request)
                # db.session.commit()

                flash(f"تم تقديم طلب السحب بنجاح برقم مرجعي ({request_code}). سيتم مراجعته وتحويل المبلغ قريباً.", "success")
                return redirect(url_for('supplier_wallet.withdraw_request'))

        except ValueError:
            flash("يرجى إدخال قيمة مالية صالحة لمبلغ السحب.", "error")

    # 3. جلب وتطبيق الترقيم لطلبات السحب السابقة (GET Method)
    status_filter = request.args.get('status', 'all')
    
    all_mock_withdrawals = _generate_mock_withdrawals()
    filtered_withdrawals = [
        w for w in all_mock_withdrawals
        if status_filter == 'all' or w['status'] == status_filter
    ]

    total_items = len(filtered_withdrawals)
    total_pages = (total_items + per_page - 1) // per_page or 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = filtered_withdrawals[start_idx:end_idx]

    class MockPagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1
            self.next_num = page + 1

        def iter_pages(self, left_edge=1, left_current=2, right_current=2, right_edge=1):
            for i in range(1, self.pages + 1):
                yield i

    pagination = MockPagination(page_items, page, per_page, total_items, total_pages)

    formatted_withdrawals = [
        WalletTableComponent.format_withdrawal_row(_DictToObj(w))
        for w in pagination.items
    ]

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        pagination=pagination,
        withdrawals=formatted_withdrawals,
        status_filter=status_filter
    )


# فئة تحويل القاموس إلى كائن لتسهيل الوصول للخلاصات trx.amount بدلاً من trx['amount']
class _DictToObj:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if key == 'created_at' and isinstance(value, str):
                try:
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M')
                except ValueError:
                    pass
            setattr(self, key, value)


def _generate_mock_transactions():
    """بيانات تجريبية لحركات المحفظة لأغراض العرض واختبار الترقيم (10 عناصر/صفحة)"""
    return [
        {'id': 1, 'reference_code': 'TRX-10025', 'amount': 4500.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'مستحقات طلبية ملابس رقم #ORD-8812', 'created_at': '2026-08-11 14:30'},
        {'id': 2, 'reference_code': 'TRX-10024', 'amount': 1200.00, 'trx_type': 'debit', 'status': 'completed', 'description': 'سحب رصيد إلى محفظة فودافون كاش', 'created_at': '2026-08-10 09:15'},
        {'id': 3, 'reference_code': 'TRX-10023', 'amount': 8300.00, 'trx_type': 'credit', 'status': 'pending', 'description': 'أرباح توريد شحنة أجهزة إلكترونية #ORD-8790', 'created_at': '2026-08-09 18:45'},
        {'id': 4, 'reference_code': 'TRX-10022', 'amount': 3100.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'تسوية عمولات مبيعات شهر يوليو', 'created_at': '2026-08-08 11:20'},
        {'id': 5, 'reference_code': 'TRX-10021', 'amount': 5000.00, 'trx_type': 'debit', 'status': 'completed', 'description': 'تحويل بنكي - البنك الأهلي المصري', 'created_at': '2026-08-05 16:00'},
        {'id': 6, 'reference_code': 'TRX-10020', 'amount': 6200.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'مستحقات طلبية أحذية رقم #ORD-8701', 'created_at': '2026-08-03 13:10'},
        {'id': 7, 'reference_code': 'TRX-10019', 'amount': 1500.00, 'trx_type': 'debit', 'status': 'cancelled', 'description': 'طلب سحب رصيد ملغى برغبة المورد', 'created_at': '2026-08-01 10:00'},
        {'id': 8, 'reference_code': 'TRX-10018', 'amount': 9400.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'تسوية طلبات جملة المورد العودة للمدارس', 'created_at': '2026-07-28 17:30'},
        {'id': 9, 'reference_code': 'TRX-10017', 'amount': 2800.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'مستحقات طلبية إكسسوارات #ORD-8650', 'created_at': '2026-07-25 15:40'},
        {'id': 10, 'reference_code': 'TRX-10016', 'amount': 3000.00, 'trx_type': 'debit', 'status': 'completed', 'description': 'سحب رصيد عبر إنستا باي (InstaPay)', 'created_at': '2026-07-22 12:15'},
        # عناصر الصفحة الثانية اختباريّاً للترقيم (الصفحة 2)
        {'id': 11, 'reference_code': 'TRX-10015', 'amount': 5300.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'مستحقات توريد بضاعة للمستودع الرئيسي', 'created_at': '2026-07-18 11:00'},
        {'id': 12, 'reference_code': 'TRX-10014', 'amount': 4000.00, 'trx_type': 'debit', 'status': 'completed', 'description': 'تحويل بنكي - بنك مصر', 'created_at': '2026-07-15 14:20'},
        {'id': 13, 'reference_code': 'TRX-10013', 'amount': 7100.00, 'trx_type': 'credit', 'status': 'completed', 'description': 'أرباح شحنة مفروشات منزلية #ORD-8510', 'created_at': '2026-07-10 09:50'},
        {'id': 14, 'reference_code': 'TRX-10012', 'amount': 1800.00, 'trx_type': 'debit', 'status': 'completed', 'description': 'سحب رصيد إلى فودافون كاش', 'created_at': '2026-07-05 16:30'}
    ]


def _generate_mock_withdrawals():
    """بيانات تجريبية لسجل طلبات السحب"""
    return [
        {'id': 1, 'request_code': 'WD-9901', 'amount': 2500.00, 'method': 'vodafone_cash', 'account_details': '01012345678', 'notes': 'سحب عاجل', 'status': 'pending', 'created_at': '2026-08-11 16:00'},
        {'id': 2, 'request_code': 'WD-9884', 'amount': 5000.00, 'method': 'bank_transfer', 'account_details': 'EG380002000100000123456789 (البنك الأهلي)', 'notes': 'تحويل أسبوعي', 'status': 'approved', 'created_at': '2026-08-05 10:30'},
        {'id': 3, 'request_code': 'WD-9752', 'amount': 3000.00, 'method': 'instapay', 'account_details': 'mahjoub@instapay', 'notes': '', 'status': 'approved', 'created_at': '2026-07-22 14:15'},
        {'id': 4, 'request_code': 'WD-9610', 'amount': 1500.00, 'method': 'vodafone_cash', 'account_details': '01098765432', 'notes': 'طلب ملغى بطلب المورد', 'status': 'cancelled', 'created_at': '2026-08-01 11:00'},
        {'id': 5, 'request_code': 'WD-9503', 'amount': 4000.00, 'method': 'bank_transfer', 'account_details': 'EG120003000100000987654321 (بنك مصر)', 'notes': '', 'status': 'approved', 'created_at': '2026-07-15 09:00'},
        {'id': 6, 'request_code': 'WD-9411', 'amount': 1800.00, 'method': 'stc_pay', 'account_details': '0501234567', 'notes': 'تحويل حساب تجاري', 'status': 'approved', 'created_at': '2026-07-05 18:20'},
        {'id': 7, 'request_code': 'WD-9302', 'amount': 6000.00, 'method': 'bank_transfer', 'account_details': 'EG550001000100000444333222 (CIB)', 'notes': 'بيانات البنك غير مطابقة للحساب', 'status': 'rejected', 'created_at': '2026-06-28 13:10'},
        {'id': 8, 'request_code': 'WD-9201', 'amount': 3500.00, 'method': 'vodafone_cash', 'account_details': '01012345678', 'notes': '', 'status': 'approved', 'created_at': '2026-06-18 10:45'},
        {'id': 9, 'request_code': 'WD-9105', 'amount': 2000.00, 'method': 'instapay', 'account_details': 'mahjoub_online@instapay', 'notes': '', 'status': 'approved', 'created_at': '2026-06-10 15:30'},
        {'id': 10, 'request_code': 'WD-9004', 'amount': 4500.00, 'method': 'bank_transfer', 'account_details': 'EG380002000100000123456789', 'notes': 'تحويل نهائي', 'status': 'approved', 'created_at': '2026-06-01 11:00'},
        # عنصر الصفحة الثانية للتجربة
        {'id': 11, 'request_code': 'WD-8990', 'amount': 3000.00, 'method': 'vodafone_cash', 'account_details': '01012345678', 'notes': 'طلب قديم', 'status': 'approved', 'created_at': '2026-05-20 14:00'}
    ]
