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


# ✅ دالة مركزية لتحديث الرصيد - عملة واحدة فقط SAR
def update_wallet_balance(wallet, amount, trans_type):
    """تحديث رصيد المحفظة بناءً على نوع العملية (العملة: SAR فقط)."""
    if trans_type == 'credit':  # إيداع (زيادة الرصيد)
        wallet.balance_sar += amount
    elif trans_type == 'debit':  # سحب (إنقاص الرصيد)
        wallet.balance_sar -= amount
    
    wallet.updated_at = func.now()
    return wallet


# 1. مسار خاص بالموردين
@wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def my_wallet():
    if session.get('user_type') != 'supplier':
        abort(403)
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    return render_template('suppliers/my_wallet.html', wallet=wallet)


# 2. مسارات الإدارة
@wallet_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%')
        ))
    
    # ✅ إحصائيات - عملة واحدة فقط SAR
    stats = {
        'total_sar': query.with_entities(func.sum(SupplierWallet.balance_sar)).scalar() or 0
    }
    
    pagination = query.order_by(SupplierWallet.id.desc()).paginate(page=page, per_page=20, error_out=False)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', wallets=pagination.items)
        
    return render_template('admin/wallet_app.html', wallets=pagination.items, stats=stats, pagination=pagination)


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
        # ✅ العملة ثابتة SAR
        currency = 'SAR'
        description = request.form.get('description', f"تسوية يدوية للطلب {order_ref}")
        
        if amount <= 0:
            flash("يجب أن يكون المبلغ أكبر من صفر.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))

        # 1. تحديث الرصيد باستخدام الدالة المركزية (بدون عملة)
        wallet = update_wallet_balance(wallet, amount, trans_type)
        
        # 2. تسجيل العملية
        new_trans = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            trans_type=trans_type,
            owner_type='supplier',
            owner_id=wallet.supplier_id,
            description=description,
            currency=currency,  # ✅ ثابت SAR
            related_order_id=order_ref if order_ref else None,
            reference_number=order_ref if order_ref else None
        )
        
        db.session.add(new_trans)
        db.session.add(wallet)
        db.session.commit()
        
        flash("تم تسجيل العملية وتحديث الرصيد بنجاح.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Financial Error: {e}")
        flash("حدث خطأ أثناء تنفيذ العملية المالية.", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
