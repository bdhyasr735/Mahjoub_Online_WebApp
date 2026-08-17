# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, url_for
from apps.models import SupplierWallet, WalletTransaction, Supplier, db
from sqlalchemy import or_, func
from decimal import Decimal
from datetime import datetime

bp = Blueprint('admin_suppliers_wallets', __name__)

PER_PAGE = 10

@bp.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    bank_filter = request.args.get('bank', 'all', type=str)

    # ✅ اكتشاف ما إذا كان الطلب قادماً من AJAX (للبحث اللحظي دون تحديث)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    query = SupplierWallet.query.join(Supplier, Supplier.id == SupplierWallet.supplier_id)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                SupplierWallet.wallet_code.ilike(search_term),
                Supplier.supplier_code.ilike(search_term),
                Supplier.store_name.ilike(search_term),
                Supplier.trade_name.ilike(search_term),
                Supplier.owner_name.ilike(search_term),
                Supplier.username.ilike(search_term)
            )
        )

    if status_filter and status_filter != 'all':
        query = query.filter(SupplierWallet.status == status_filter)

    if bank_filter and bank_filter != 'all':
        query = query.filter(Supplier.bank_name.ilike(f"%{bank_filter}%"))

    query = query.order_by(SupplierWallet.id.desc())

    total_sar_balance = db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or Decimal('0.00')
    total_pending_balance = db.session.query(func.sum(SupplierWallet.balance_pending)).scalar() or Decimal('0.00')
    pending_withdrawals_amount = db.session.query(func.sum(WalletTransaction.amount)).filter_by(status='pending').scalar() or Decimal('0.00')
    total_wallets_balance = Decimal(str(total_sar_balance)) + Decimal(str(total_pending_balance))

    kpis = {
        'total_wallets_balance': total_wallets_balance,
        'total_available_payouts': total_sar_balance,
        'total_escrow_held': total_pending_balance,
        'total_suppliers_count': SupplierWallet.query.count(),
        'active_suppliers_count': SupplierWallet.query.filter_by(status='active').count(),
        'pending_withdrawals_amount': pending_withdrawals_amount,
        'pending_withdrawals_count': WalletTransaction.query.filter_by(status='pending').count()
    }

    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    suppliers = pagination_obj.items

    pagination = {
        'current_page': pagination_obj.page,
        'total_pages': pagination_obj.pages,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'total_count': pagination_obj.total,
        'per_page': PER_PAGE,
        'prev_num': pagination_obj.prev_num,
        'next_num': pagination_obj.next_num,
    }

    if is_ajax:
        return render_template(
            'admin/suppliers_wallets.html',
            kpis=kpis,
            pagination=pagination,
            suppliers=suppliers,
            search_query=search_query,
            status_filter=status_filter,
            bank_filter=bank_filter
        )

    return render_template(
        'admin/suppliers_wallets.html',
        kpis=kpis,
        pagination=pagination,
        suppliers=suppliers,
        search_query=search_query,
        status_filter=status_filter,
        bank_filter=bank_filter
    )

@bp.route('/<int:supplier_id>', methods=['GET'])
def supplier_ledger_detail(supplier_id):
    wallet = SupplierWallet.query.get_or_404(supplier_id)
    page = request.args.get('page', 1, type=int)
    
    transactions_pagination = WalletTransaction.query.filter_by(
        wallet_id=wallet.id,
        status='completed'
    ).order_by(WalletTransaction.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template(
        'admin/supplier_ledger_detail.html',
        wallet=wallet,
        transactions_pagination=transactions_pagination
    )

@bp.route('/<int:supplier_id>/adjust', methods=['POST'])
def adjust_wallet_balance(supplier_id):
    try:
        data = request.get_json()
        trans_type = 'deposit' if data.get('type') == 'credit' else 'withdraw'
        amount = Decimal(str(data.get('amount', 0)))
        description = data.get('description', 'تسوية يدوية')

        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'يجب أن يكون المبلغ أكبر من 0.'})

        wallet = SupplierWallet.query.get_or_404(supplier_id)

        if wallet.status == 'frozen':
            return jsonify({'status': 'error', 'message': 'لا يمكن إجراء حركات مالية على محفظة مجمدة.'})

        current_balance = Decimal(str(wallet.balance_sar))
        new_balance = current_balance + amount if trans_type == 'deposit' else current_balance - amount

        new_transaction = WalletTransaction(
            wallet_id=wallet.id,
            trans_type=trans_type,
            status='completed',
            amount=amount,
            currency='SAR',
            balance_before=current_balance,
            balance_after=new_balance
        )
        new_transaction.description = description
        db.session.add(new_transaction)

        wallet.balance_sar = new_balance
        wallet.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'تم قيد الحركة المالية بنجاح.',
            'voucher_code': f"VCH-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            'ref_code': f"REF-{wallet.id}-{datetime.utcnow().strftime('%H%M')}",
            'new_balance': float(new_balance)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'حدث خطأ: {str(e)}'})

@bp.route('/<int:supplier_id>/toggle_freeze', methods=['POST'])
def toggle_wallet_freeze(supplier_id):
    try:
        data = request.get_json()
        wallet = SupplierWallet.query.get_or_404(supplier_id)
        
        new_status = 'frozen' if wallet.status == 'active' else 'active'
        wallet.status = new_status
        wallet.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'تم تغيير حالة المحفظة إلى {"مجمدة" if new_status == "frozen" else "نشطة"} بنجاح.',
            'new_status': new_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'حدث خطأ: {str(e)}'})
