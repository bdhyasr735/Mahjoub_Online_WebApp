# coding: utf-8
# 🏦 بلوبرينت المحفظة المالية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from datetime import datetime
import os

# تعريف البلوبرينت
wallet_blueprint = Blueprint('wallet', __name__)

@wallet_blueprint.route('/management', methods=['GET'])
@login_required
def display_management_table():
    search_query = request.args.get('search_query', '')
    wallet = None
    wallet_settlements = []
    pending_withdrawals = []

    # حساب إحصائيات النظام العامة
    total_wallets_count = SupplierWallet.query.count()
    total_yer_system = db.session.query(db.func.sum(SupplierWallet.yer_total)).scalar() or 0
    total_sar_system = db.session.query(db.func.sum(SupplierWallet.sar_total)).scalar() or 0
    total_usd_system = db.session.query(db.func.sum(SupplierWallet.usd_total)).scalar() or 0

    if search_query:
        wallet = SupplierWallet.query.filter(
            (SupplierWallet.supplier_id == search_query) | 
            (SupplierWallet.wallet_code == search_query)
        ).first()
        
        if wallet:
            wallet_settlements = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
                .order_by(WalletTransaction.created_at.desc()).all()
            pending_withdrawals = WalletTransaction.query.filter_by(wallet_id=wallet.id, status='معلقة').all()

    # استخدام المسار الكامل للمجلد للتحايل على مشاكل التوجيه
    return render_template('admin/settlement_and_withdrawal.html',
                           total_wallets_count=total_wallets_count,
                           total_yer_system=total_yer_system,
                           total_sar_system=total_sar_system,
                           total_usd_system=total_usd_system,
                           wallet=wallet,
                           wallet_settlements=wallet_settlements,
                           pending_withdrawals=pending_withdrawals,
                           current_search=search_query)

@wallet_blueprint.route('/execute-settlement/<wallet_code>', methods=['POST'])
@login_required
def execute_admin_settlement(wallet_code):
    wallet = SupplierWallet.query.filter_by(wallet_code=wallet_code).first_or_404()
    
    tx_type = request.form.get('settlement_type')
    currency = request.form.get('currency')
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        amount = 0

    # تحديث الأرصدة
    if tx_type == 'deposit':
        if currency == 'YER': wallet.yer_total = (wallet.yer_total or 0) + amount
        elif currency == 'SAR': wallet.sar_total = (wallet.sar_total or 0) + amount
        elif currency == 'USD': wallet.usd_total = (wallet.usd_total or 0) + amount
    else:
        if currency == 'YER': wallet.yer_withdrawn = (wallet.yer_withdrawn or 0) + amount
        elif currency == 'SAR': wallet.sar_withdrawn = (wallet.sar_withdrawn or 0) + amount
        elif currency == 'USD': wallet.usd_withdrawn = (wallet.usd_withdrawn or 0) + amount

    # تسجيل الحركة
    new_tx = WalletTransaction(
        wallet_id=wallet.id,
        tx_code=f"ADM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        tx_type=f"تسوية إدارية ({tx_type})",
        currency=currency,
        amount=amount,
        financial_entity=request.form.get('financial_entity', 'الإدارة المركزية'),
        reference_number=request.form.get('reference_number', 'N/A'),
        notes=request.form.get('notes', ''),
        status='ناجحة',
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_tx)
    db.session.commit()
    flash(f"تم اعتماد سند التسوية: {new_tx.tx_code}", "success")
    return redirect(url_for('wallet.display_management_table', search_query=wallet_code))

@wallet_blueprint.route('/handle-withdrawal/<int:tx_id>/<decision>', methods=['POST'])
@login_required
def handle_supplier_withdrawal(tx_id, decision):
    tx = WalletTransaction.query.get_or_404(tx_id)
    wallet = SupplierWallet.query.get(tx.wallet_id)
    
    if decision == 'approve':
        tx.status = 'ناجحة'
        if tx.currency == 'YER': 
            wallet.yer_pending = (wallet.yer_pending or 0) - tx.amount
            wallet.yer_withdrawn = (wallet.yer_withdrawn or 0) + tx.amount
        elif tx.currency == 'SAR':
            wallet.sar_pending = (wallet.sar_pending or
