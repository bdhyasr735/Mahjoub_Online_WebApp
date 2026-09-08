# coding: utf-8
# 📂 apps/wallet/routes.py - إدارة محافظ الموردين

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, func

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, generate_unique_voucher_number
from apps.models.supplier_db import Supplier

logger = logging.getLogger(__name__)

# ✅ اسم البلوبريت
wallet_bp = Blueprint('wallet_app', __name__, template_folder='templates')


# ✅ دالة مركزية لتحديث الرصيد
def update_wallet_balance(wallet, amount, trans_type):
    """تحديث رصيد المحفظة بناءً على نوع العملية (العملة: SAR فقط)."""
    if trans_type == 'credit':  # إيداع (زيادة الرصيد)
        wallet.balance += amount
    elif trans_type == 'debit':  # سحب أو خصم (إنقاص الرصيد)
        wallet.balance -= amount
    
    # تحديث تاريخ التعديل
    wallet.updated_at = datetime.utcnow()
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
    
    # ✅ استعلام أساسي
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    # ✅ البحث اللحظي الشامل: أرقام، نصوص، ورموز
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            Supplier.owner_name.ilike(f'%{search}%'),
            Supplier.supplier_code.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%'),
            SupplierWallet.id.cast(db.String).ilike(f'%{search}%')  # البحث بالرقم
        ))
    
    # ✅ إحصائيات
    stats = {
        'total_sar': query.with_entities(func.sum(SupplierWallet.balance)).scalar() or 0
    }
    
    # ✅ كل 10 موردين كصفحة
    pagination = query.order_by(SupplierWallet.id.desc()).paginate(page=page, per_page=10, error_out=False)
    
    # ✅ عند طلب AJAX: إرجاع الجدول كاملاً مع الترقيم من الملف الجديد
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/wallet_table_ajax.html', wallets=pagination.items, pagination=pagination)
        
    return render_template('admin/wallet_app.html', wallets=pagination.items, stats=stats, pagination=pagination)


@wallet_bp.route('/admin/manage/<string:supplier_code>', methods=['GET'])
@login_required
def manage_wallet(supplier_code):
    # البحث عن المورد بواسطة كود المورد
    supplier = Supplier.query.filter_by(supplier_code=supplier_code).first_or_404()
    
    # البحث عن المحفظة المرتبطة بهذا المورد
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first_or_404()
    
    return render_template('admin/view_wallet.html', wallet=wallet)


@wallet_bp.route('/admin/manage/<string:supplier_code>/add_transaction', methods=['POST'])
@login_required
def add_transaction(supplier_code):
    # البحث عن المورد بواسطة كود المورد
    supplier = Supplier.query.filter_by(supplier_code=supplier_code).first_or_404()
    
    # البحث عن المحفظة المرتبطة بهذا المورد
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first_or_404()
    
    try:
        amount_raw = request.form.get('amount', '0')
        try:
            amount = Decimal(amount_raw)
        except InvalidOperation:
            flash("قيمة المبلغ غير صحيحة.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_code=supplier_code))
            
        trans_type = request.form.get('type')  # 'credit' أو 'debit'
        order_ref = request.form.get('reference_number', '').strip()
        # ✅ العملة ثابتة SAR (مأخوذة من المحفظة)
        currency = wallet.currency or 'SAR'
        description = request.form.get('description', f"تسوية يدوية للطلب {order_ref}")
        
        if amount <= 0:
            flash("يجب أن يكون المبلغ أكبر من صفر.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_code=supplier_code))

        # 1. تحديث الرصيد
        wallet = update_wallet_balance(wallet, amount, trans_type)
        
        # 2. توليد رقم سند فريد
        generated_voucher = generate_unique_voucher_number()

        # 3. تسجيل العملية
        new_trans = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=trans_type,
            voucher_number=generated_voucher,
            description=f"{description} | مرجع بنكي: {order_ref if order_ref else 'N/A'}"
        )
        
        db.session.add(new_trans)
        db.session.add(wallet)
        db.session.commit()
        
        flash("تم تسجيل العملية وتحديث الرصيد بنجاح.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Financial Error: {e}")
        flash("حدث خطأ أثناء تنفيذ العملية المالية.", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_code=supplier_code))
