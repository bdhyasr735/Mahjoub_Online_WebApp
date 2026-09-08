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

# ✅ تصحيح اسم البلوبريت ليتوافق مع registry.py
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
    
    # ✅ تعديل الاستعلام: دمج الجداول بشكل صحيح
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%')
        ))
    
    # ✅ إحصائيات - استخدام الحقل الصحيح (balance)
    stats = {
        'total_sar': query.with_entities(func.sum(SupplierWallet.balance)).scalar() or 0
    }
    
    pagination = query.order_by(SupplierWallet.id.desc()).paginate(page=page, per_page=20, error_out=False)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', wallets=pagination.items)
        
    return render_template('admin/wallet_app.html', wallets=pagination.items, stats=stats, pagination=pagination)


# ✅ تم تعديل هذا المسار ليقبل "كود المورد" (supplier_code) بدلاً من الرقم
@wallet_bp.route('/admin/manage/<string:supplier_code>', methods=['GET'])
@login_required
def manage_wallet(supplier_code):
    # البحث عن المورد بواسطة كود المورد
    supplier = Supplier.query.filter_by(supplier_code=supplier_code).first_or_404()
    
    # البحث عن المحفظة المرتبطة بهذا المورد
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first_or_404()
    
    return render_template('admin/view_wallet.html', wallet=wallet)


# ✅ تم تعديل هذا المسار أيضاً ليقبل "كود المورد" (supplier_code)
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

        # 1. تحديث الرصيد (باستخدام الحقل الصحيح balance بدلاً من balance_sar)
        wallet = update_wallet_balance(wallet, amount, trans_type)
        
        # 2. توليد رقم سند فريد تلقائياً (لضمان عدم تكرار مشكلة المرجع المفقود)
        # إذا أدخل الأدمن رقم حوالة بنكية، نستخدمه في الـ description، لكننا ننشئ سنداً داخلياً خاصاً بنا
        generated_voucher = generate_unique_voucher_number()

        # 3. تسجيل العملية باستخدام الحقول الصحيحة من wallet_db.py
        new_trans = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=trans_type,  # ✅ حقل صحيح
            voucher_number=generated_voucher,  # ✅ رقم السند الداخلي
            description=f"{description} | مرجع بنكي: {order_ref if order_ref else 'N/A'}"  # ✅ وضع المرجع البنكي في الوصف
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
