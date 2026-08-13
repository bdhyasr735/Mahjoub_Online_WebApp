# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import get_current_supplier_id, get_or_create_supplier_wallet

@supplier_wallet_bp.route('/', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/wallet', methods=['GET'], strict_slashes=False)
@login_required
def wallet():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # تجهيز ملخص المحفظة مباشرة من الموديل
    summary = {
        'total_balance': float(wallet_obj.balance_sar or 0.0),
        'available_balance': float(wallet_obj.balance_sar or 0.0),
        'pending_balance': float(wallet_obj.balance_pending or 0.0),
        'total_withdrawn': float(wallet_obj.total_withdrawn or 0.0),
        'currency': 'SAR',
        'min_withdraw_amount': 50.00
    }

    # معالجة الفلاتر وعرض المعاملات
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10
    
    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id)

    # فلترة حسب النوع والحالة
    trx_type = request.args.get('type', 'all')
    if trx_type != 'all':
        query = query.filter(WalletTransaction.trans_type == trx_type)

    status = request.args.get('status', 'all')
    if status != 'all':
        query = query.filter(WalletTransaction.status == status)
    else:
        # افتراضياً إخفاء المعلقات إذا لم يطلب المستخدم رؤيتها
        query = query.filter(WalletTransaction.status != 'pending')

    # بحث
    search_query = request.args.get('search', '').strip()
    if search_query:
        from sqlalchemy import or_
        query = query.filter(or_(
            WalletTransaction.reference_number.ilike(f"%{search_query}%"),
            WalletTransaction.voucher_number.ilike(f"%{search_query}%"),
            WalletTransaction.description.ilike(f"%{search_query}%")
        ))

    # التاريخ
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    if from_date:
        query = query.filter(WalletTransaction.created_at >= datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(WalletTransaction.created_at <= datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))

    pagination_obj = query.order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        wallet=summary,
        transactions=pagination_obj.items,
        pagination=pagination_obj
    )
