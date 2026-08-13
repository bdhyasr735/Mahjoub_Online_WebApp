# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_trx_type_attr, 
    get_status_attr
)

@supplier_wallet_bp.route('/', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/wallet', methods=['GET'], strict_slashes=False)
@login_required
def wallet():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    if wallet_obj:
        wallet_id = wallet_obj.id
        
        q_completed = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_completed = q_completed.filter(status_col == 'completed')
        if trx_type_col is not None:
            q_completed = q_completed.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit']))
        completed_credits = q_completed.scalar() or 0.00

        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_pending = q_pending.filter(status_col == 'pending')
        if trx_type_col is not None:
            q_pending = q_pending.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit', 'withdrawal', 'debit']))
        pending_credits = q_pending.scalar() or 0.00

        # حصر إجمالي المسحوبات على الحركات المكتملة فقط (completed)
        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_withdrawn = q_withdrawn.filter(status_col == 'completed')
        if trx_type_col is not None:
            q_withdrawn = q_withdrawn.filter(trx_type_col.in_(['withdrawal', 'debit']))
        total_withdrawn = q_withdrawn.scalar() or 0.00

        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            avail_bal = max(0.00, float(getattr(wallet_obj, 'balance_sar', 0.00)))

        tot_bal = avail_bal + float(pending_credits)

        summary = {
            'total_balance': float(tot_bal),
            'available_balance': float(avail_bal),
            'pending_balance': float(pending_credits),
            'total_withdrawn': float(total_withdrawn),
            'currency': getattr(wallet_obj, 'currency', 'SAR'),
            'min_withdraw_amount': 50.00
        }
    else:
        summary = {
            'total_balance': 0.00, 'available_balance': 0.00,
            'pending_balance': 0.00, 'total_withdrawn': 0.00, 'currency': 'SAR',
            'min_withdraw_amount': 50.00
        }

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10
    
    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    trx_type = request.args.get('type', 'all')
    if trx_type != 'all' and trx_type_col is not None:
        query = query.filter(trx_type_col == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all' and status_col is not None:
        query = query.filter(status_col == status)
    elif status_col is not None:
        query = query.filter(status_col != 'pending')

    search_query = request.args.get('search', '').strip()
    if search_query:
        search_filters = []
        for col in ['reference_number', 'voucher_number', 'description']:
            if hasattr(WalletTransaction, col):
                search_filters.append(getattr(WalletTransaction, col).ilike(f"%{search_query}%"))
        if search_filters:
            from sqlalchemy import or_
            query = query.filter(or_(*search_filters))

    from_date_str = request.args.get('from_date', '').strip()
    to_date_str = request.args.get('to_date', '').strip()

    if from_date_str and hasattr(WalletTransaction, 'created_at'):
        try:
            query = query.filter(WalletTransaction.created_at >= datetime.strptime(from_date_str, '%Y-%m-%d'))
        except ValueError:
            pass

    if to_date_str and hasattr(WalletTransaction, 'created_at'):
        try:
            to_date_end = datetime.strptime(to_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(WalletTransaction.created_at <= to_date_end)
        except ValueError:
            pass

    if hasattr(WalletTransaction, 'created_at'):
        query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())
    else:
        query = query.order_by(WalletTransaction.id.desc())

    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    class PaginationWrapper:
        def __init__(self, p_obj, per_page):
            self.items = p_obj.items
            self.page = p_obj.page
            self.pages = p_obj.pages
            self.total_pages = p_obj.pages
            self.total = p_obj.total
            self.total_items = p_obj.total
            self.has_prev = p_obj.has_prev
            self.has_next = p_obj.has_next
            self.per_page = per_page
            self._p_obj = p_obj

        def iter_pages(self, *args, **kwargs):
            if hasattr(self._p_obj, 'iter_pages'):
                return self._p_obj.iter_pages(*args, **kwargs)
            return []

    pagination = PaginationWrapper(pagination_obj, PER_PAGE)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        wallet=summary,
        pagination=pagination,
        pagination_obj=pagination_obj
    )


@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    registered_owner = getattr(wallet_obj, 'owner_name', None) or getattr(wallet_obj, 'supplier_name', 'مورد معتمد')
    registered_details = getattr(wallet_obj, 'bank_details', None) or getattr(wallet_obj, 'account_details', 'حساب بنكي مسجل وموثق')

    avail_bal = getattr(wallet_obj, 'available_balance', None)
    if avail_bal is None:
        avail_bal = max(0.00, float(getattr(wallet_obj, 'balance_sar', 0.00)))

    summary = {
        'available_balance': float(avail_bal),
        'min_withdraw_amount': 50.00,
        'currency': getattr(wallet_obj, 'currency', 'SAR')
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank')

            if amount < summary['min_withdraw_amount']:
                flash(f"الحد الأدنى للسحب هو {summary['min_withdraw_amount']} SAR", "danger")
            elif amount > summary['available_balance']:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح للسحب", "danger")
            else:
                ref_no = f"WD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                desc = f"طلب سحب أرباح عبر {'تحويل بنكي' if method == 'bank' else 'شركات الصرافة'}"
                
                new_tx = WalletTransaction(
                    wallet_id=wallet_obj.id if wallet_obj else None,
                    amount=amount,
                    reference_number=ref_no,
                    description=desc,
                    owner_name=registered_owner
                )
                if trx_type_col is not None:
                    setattr(new_tx, trx_type_col.key, 'withdrawal')
                if status_col is not None:
                    setattr(new_tx, status_col.key, 'pending')

                db.session.add(new_tx)
                
                if hasattr(wallet_obj, 'available_balance'):
                    wallet_obj.available_balance -= amount
                elif hasattr(wallet_obj, 'balance_sar'):
                    wallet_obj.balance_sar -= amount

                db.session.commit()
                flash("تم تقديم طلب السحب بنجاح وهو قيد المراجعة.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء معالجة طلب السحب: {str(e)}", "danger")

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)
    if trx_type_col is not None:
        query = query.filter(trx_type_col.in_(['withdrawal', 'debit']))

    status_filter = request.args.get('status', 'all')
    if status_filter != 'all' and status_col is not None:
        query = query.filter(status_col == status_filter)

    if hasattr(WalletTransaction, 'created_at'):
        query = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc())
    else:
        query = query.order_by(WalletTransaction.id.desc())

    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    class PaginationWrapper:
        def __init__(self, p_obj, per_page):
            self.items = p_obj.items
            self.page = p_obj.page
            self.pages = p_obj.pages
            self.total_pages = p_obj.pages
            self.total = p_obj.total
            self.total_items = p_obj.total
            self.has_prev = p_obj.has_prev
            self.has_next = p_obj.has_next
            self.per_page = per_page
            self._p_obj = p_obj

        def iter_pages(self, *args, **kwargs):
            if hasattr(self._p_obj, 'iter_pages'):
                return self._p_obj.iter_pages(*args, **kwargs)
            return []

    pagination = PaginationWrapper(pagination_obj, PER_PAGE)
    withdrawals = pagination.items

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        registered_owner=registered_owner,
        registered_details=registered_details,
        withdrawals=withdrawals,
        pagination=pagination
    )
