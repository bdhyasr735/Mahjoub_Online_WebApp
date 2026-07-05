# coding: utf-8
# 📂 apps/wallet/routes.py - إدارة محافظ الموردين (الإدارة)

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.extensions import db
from sqlalchemy import or_, func
from decimal import Decimal, InvalidOperation

# إعداد المسجل (Logger)
logger = logging.getLogger(__name__)

# تعريف البلوبرنت
wallet_bp = Blueprint('wallet_app', __name__, template_folder='templates')

@wallet_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الإدارة: عرض محافظ الموردين مع دعم البحث الشامل والترقيم."""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    # 1. إنشاء استعلام أساسي
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    # 2. تطبيق الفلترة (بحث شامل)
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%')
        ))
    
    # 3. حساب الإجماليات بناءً على نتيجة البحث (وليس كل القاعدة)
    stats = {
        'total_sar': query.with_entities(func.sum(SupplierWallet.balance_sar)).scalar() or 0,
        'total_yer': query.with_entities(func.sum(SupplierWallet.balance_yer)).scalar() or 0,
        'total_usd': query.with_entities(func.sum(SupplierWallet.balance_usd)).scalar() or 0
    }
    
    # 4. تنفيذ الترقيم (20 مورد لكل صفحة)
    wallets = query.order_by(SupplierWallet.id.desc()).paginate(page=page, per_page=20, error_out=False)
    
    # 5. استجابة AJAX لتحديث الجدول فقط
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', wallets=wallets.items, pagination=wallets)
        
    return render_template(
        'admin/wallet_app.html', 
        wallets=wallets.items, 
        stats=stats,
        pagination=wallets
    )

@wallet_bp.route('/admin/manage/<int:supplier_id>', methods=['GET'])
@login_required
def manage_wallet(supplier_id):
    """عرض كشف الحساب التفصيلي لمورد معين."""
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    return render_template('admin/view_wallet.html', wallet=wallet)

@wallet_bp.route('/admin/manage/<int:supplier_id>/add_transaction', methods=['POST'])
@login_required
def add_transaction(supplier_id):
    """إضافة حركة مالية يدوية."""
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

        new_trans = WalletTransaction.execute_transfer(
            wallet_id=wallet.id,
            amount=amount,
            trans_type=trans_type,
            owner_type='supplier',
            owner_id=wallet.supplier_id,
            description=description
        )
        
        new_trans.currency = currency
        new_trans.related_order_id = order_ref if order_ref else None
        new_trans.reference_number = order_ref if order_ref else None
        
        db.session.commit()
        logger.info(f"Financial Audit: Wallet ID {wallet.id} | Amount: {amount} {currency}")
        flash(f"تم تسجيل العملية بنجاح للمورد: {wallet.supplier.trade_name}", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Financial Error for supplier {supplier_id}: {e}")
        flash(f"حدث خطأ: {str(e)}", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
