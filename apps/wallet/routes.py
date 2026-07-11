# coding: utf-8
# 📂 apps/wallet/routes.py - إدارة محافظ الموردين

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.extensions import db
from sqlalchemy import or_, func
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

# تعريف البلوبرنت
wallet_bp = Blueprint('wallet_app', __name__, template_folder='templates')

# 1. مسار خاص بالموردين (لحل مشكلة /supplier/wallet/my-wallet)
@wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def my_wallet():
    """عرض محفظة المورد الحالي."""
    if session.get('user_type') != 'supplier':
        abort(403)
        
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    return render_template('suppliers/my_wallet.html', wallet=wallet)

# 2. مسارات الإدارة
@wallet_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    # تأكد أن هذا الجزء مخصص للمدراء فقط إذا لزم الأمر
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%')
        ))
    
    stats = {
        'total_sar': query.with_entities(func.sum(SupplierWallet.balance_sar)).scalar() or 0,
        'total_yer': query.with_entities(func.sum(SupplierWallet.balance_yer)).scalar() or 0,
        'total_usd': query.with_entities(func.sum(SupplierWallet.balance_usd)).scalar() or 0
    }
    
    pagination = query.order_by(SupplierWallet.id.desc()).paginate(page=page, per_page=20, error_out=False)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', wallets=pagination.items)
        
    return render_template(
        'admin/wallet_app.html', 
        wallets=pagination.items, 
        stats=stats,
        pagination=pagination
    )

@wallet_bp.route('/admin/manage/<int:supplier_id>', methods=['GET'])
@login_required
def manage_wallet(supplier_id):
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)

@wallet_bp.route('/admin/manage/<int:supplier_id>/add_transaction', methods=['POST'])
@login_required
def add_transaction(supplier_id):
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    try:
        amount_raw = request.form.get('amount', '0')
        try:
            amount = Decimal(amount_raw)
        except InvalidOperation:
            flash("قيمة المبلغ غير صحيحة.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
            
        trans_type = request.form.get('type')
        order_ref = request.form.get('reference_number', '').strip()
        currency = request.form.get('currency', 'SAR')
        description = request.form.get('description', f"تسوية يدوية للطلب {order_ref}")
        
        if amount <= 0:
            flash("يجب أن يكون المبلغ أكبر من صفر.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))

        new_trans = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            trans_type=trans_type,
            owner_type='supplier',
            owner_id=wallet.supplier_id,
            description=description,
            currency=currency,
            related_order_id=order_ref if order_ref else None,
            reference_number=order_ref if order_ref else None
        )
        
        db.session.add(new_trans)
        db.session.commit()
        
        flash(f"تم تسجيل العملية بنجاح.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Financial Error: {e}")
        flash(f"حدث خطأ داخلي.", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
