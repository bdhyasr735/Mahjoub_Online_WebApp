# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request
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

        # تعديل الاستعلام ليشمل طلبات السحب والحركات المعلقة (قيد المراجعة) بجانب الإيرادات المعلقة
        q_pending = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_pending = q_pending.filter(status_col == 'pending')
        if trx_type_col is not None:
            q_pending = q_pending.filter(trx_type_col.in_(['credit', 'sale_revenue', 'deposit', 'adjustment_credit', 'withdrawal', 'debit']))
        pending_credits = q_pending.scalar() or 0.00

        q_withdrawn = db.session.query(db.func.sum(WalletTransaction.amount)).filter(WalletTransaction.wallet_id == wallet_id)
        if status_col is not None:
            q_withdrawn = q_withdrawn.filter(status_col.in_(['completed', 'pending']))
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
            'currency': getattr(wallet_obj, 'currency', 'ر.س')
        }
    else:
        summary = {
            'total_balance': 0.00, 'available_balance': 0.00,
            'pending_balance': 0.00, 'total_withdrawn': 0.00, 'currency': 'ر.س'
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
        # استبعاد الحركات المعلقة (قيد المراجعة) افتراضياً ومن "جميع الحالات" حتى يتم اعتمادها
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


@supplier_wallet_bp.route('/wallet/export-pdf', methods=['GET'], strict_slashes=False)
@login_required
def export_pdf():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    trx_type = request.args.get('type', 'all')
    if trx_type != 'all' and trx_type_col is not None:
        query = query.filter(trx_type_col == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all' and status_col is not None:
        query = query.filter(status_col == status)
    elif status_col is not None:
        query = query.filter(status_col != 'pending')

    transactions = query.order_by(WalletTransaction.id.desc()).all()

    summary = {'currency': getattr(wallet_obj, 'currency', 'ر.س') if wallet_obj else 'ر.س'}

    return render_template(
        'supplier_wallet/wallet_pdf_print.html',
        summary=summary,
        transactions=transactions,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
