# coding: utf-8
# 📂 apps/wallet/routes.py - إدارة محافظ الموردين (الإدارة)

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.extensions import db
from sqlalchemy import or_, func
from decimal import Decimal

# إعداد المسجل (Logger) لتتبع الأخطاء المالية
logger = logging.getLogger(__name__)

# تعريف البلوبرنت
wallet_bp = Blueprint('wallet_app', __name__, template_folder='templates')

@wallet_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم الإدارة: عرض كافة محافظ الموردين وإجماليات المنصة."""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    # 1. جلب بيانات المحافظ مع ربط اسم المورد للبحث
    query = SupplierWallet.query.join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            SupplierWallet.wallet_code.ilike(f'%{search}%')
        ))
    
    wallets = query.paginate(page=page, per_page=20, error_out=False)
    
    # 2. حساب الإجماليات المالية للمنصة
    stats = {
        'total_sar': db.session.query(func.sum(SupplierWallet.balance_sar)).scalar() or 0,
        'total_yer': db.session.query(func.sum(SupplierWallet.balance_yer)).scalar() or 0,
        'total_usd': db.session.query(func.sum(SupplierWallet.balance_usd)).scalar() or 0
    }
    
    # 3. دعم التحديث الديناميكي (AJAX)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/wallet_table_body.html', wallets=wallets.items, pagination=wallets)
        
    return render_template(
        'admin/wallet_app.html', 
        wallets=wallets.items, 
        stats=stats, # تمرير الإحصائيات في قاموس واحد أنظف
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
    """إضافة حركة مالية يدوية (تسوية، مكافأة، أو خصم)."""
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    try:
        # استخراج ومعالجة البيانات
        amount_raw = request.form.get('amount', 0)
        amount = Decimal(str(amount_raw))
        trans_type = request.form.get('type')  # 'credit' أو 'debit'
        order_ref = request.form.get('reference_number', '').strip()
        currency = request.form.get('currency', 'SAR')
        description = request.form.get('description', f"تسوية يدوية للطلب {order_ref}")
        
        if amount <= 0:
            flash("يجب أن يكون المبلغ أكبر من صفر.", "danger")
            return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))

        # تنفيذ العملية عبر المحرك المحاسبي الموحد
        new_trans = WalletTransaction.execute_transfer(
            wallet_id=wallet.id,
            amount=amount,
            trans_type=trans_type,
            owner_type='supplier',
            owner_id=wallet.supplier_id,
            description=description
        )
        
        # تعيين البيانات الإضافية
        new_trans.currency = currency
        new_trans.related_order_id = order_ref if order_ref else None
        new_trans.reference_number = order_ref if order_ref else None
        
        db.session.commit()
        flash(f"تم تسجيل العملية بنجاح للمورد: {wallet.supplier.trade_name}", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Financial Error for supplier {supplier_id}: {e}")
        flash(f"حدث خطأ أثناء تنفيذ العملية المالية: {str(e)}", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
