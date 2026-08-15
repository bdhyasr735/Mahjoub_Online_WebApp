# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from apps.models import SupplierWallet, WalletTransaction, db
from sqlalchemy import or_, func
from decimal import Decimal

bp = Blueprint('suppliers_wallets_controller', __name__)

PER_PAGE = 10

@bp.route('/', methods=['GET'])
def index():
    """
    الصفحة الرئيسية لوحة تحكم محافظ الموردين مع حساب دقيق للأهلّة
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    
    query = SupplierWallet.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.join(SupplierWallet.supplier).filter(
            or_(
                SupplierWallet.wallet_code.ilike(search_term),
                Supplier.supplier_name.ilike(search_term),
                Supplier.commercial_reg.ilike(search_term)
            )
        )

    if status_filter and status_filter != 'all':
        query = query.filter(SupplierWallet.status == status_filter)

    # استخدام Decimal(0) لضمان عدم ضياع أي هللة أثناء الجمع والحسابات المالية
    total_sar_balance = db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or Decimal('0.00')
    total_pending_balance = db.session.query(func.sum(SupplierWallet.balance_pending)).scalar() or Decimal('0.00')
    pending_withdrawals_amount = db.session.query(func.sum(WalletTransaction.amount)).filter_by(status='pending').scalar() or Decimal('0.00')

    # ضمان توافق الأنواع تماماً من نوع Decimal لدقة الأهلّة
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
        'per_page': PER_PAGE
    }

    return render_template(
        'admin/suppliers_wallets.html',
        kpis=kpis,
        pagination=pagination,
        suppliers=suppliers,
        search_query=search_query,
        status_filter=status_filter
    )

@bp.route('/<int:supplier_id>', methods=['GET'])
def supplier_ledger_detail(supplier_id):
    wallet = SupplierWallet.query.get_or_404(supplier_id)
    return render_template(
        'admin/supplier_ledger_detail.html',
        wallet=wallet
    )
