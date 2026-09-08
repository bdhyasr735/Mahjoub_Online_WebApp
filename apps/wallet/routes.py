# coding: utf-8
# 📂 apps/wallet/routes.py - إدارة محافظ الموردين

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, func

from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction, WithdrawalRequest, generate_unique_voucher_number
from apps.models.supplier_db import Supplier
from apps.models.treasury_db import TreasuryEntry

# ✅ استيراد قوائم البنوك والشركات
from apps.data.yemen_banks import BANKS_LIST  # افترض أن الاسم هكذا
from apps.data.financial_companies import COMPANIES_LIST  # افترض أن الاسم هكذا

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


# =========================================================
# 3. إدارة طلبات السحب (Withdrawals) - للأدمن فقط
# =========================================================

# 3.1 صفحة قائمة طلبات السحب
@wallet_bp.route('/admin/withdrawals', methods=['GET'])
@login_required
def admin_withdrawals():
    """عرض جميع طلبات السحب للموردين"""
    # التأكد من أن المستخدم هو أدمن
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
        
    search = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = WithdrawalRequest.query.join(SupplierWallet, WithdrawalRequest.wallet_id == SupplierWallet.id).join(Supplier, SupplierWallet.supplier_id == Supplier.id)
    
    if search:
        query = query.filter(or_(
            Supplier.trade_name.ilike(f'%{search}%'),
            WithdrawalRequest.request_number.ilike(f'%{search}%'),
            WithdrawalRequest.status.ilike(f'%{search}%')
        ))
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    stats = {
        'pending': WithdrawalRequest.query.filter_by(status='pending').count(),
        'completed': WithdrawalRequest.query.filter_by(status='completed').count(),
        'rejected': WithdrawalRequest.query.filter_by(status='rejected').count(),
    }
    
    pagination = query.order_by(WithdrawalRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('admin/partials/withdrawals_table_body.html', requests=pagination.items, pagination=pagination)
        
    return render_template('admin/withdrawals_list.html', requests=pagination.items, stats=stats, pagination=pagination, status_filter=status_filter)


# 3.2 صفحة تفاصيل طلب سحب واحد
@wallet_bp.route('/admin/withdrawals/<string:request_number>', methods=['GET'])
@login_required
def admin_view_withdrawal(request_number):
    """عرض تفاصيل طلب سحب معين"""
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
        
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    return render_template('admin/review_withdrawal.html', withdrawal=withdrawal, banks=BANKS_LIST, companies=COMPANIES_LIST)


# 3.3 اعتماد طلب السحب
@wallet_bp.route('/admin/withdrawals/<string:request_number>/approve', methods=['POST'])
@login_required
def approve_withdrawal(request_number):
    """اعتماد طلب السحب وخصم المبلغ من المحفظة"""
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
        
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    wallet = withdrawal.wallet
    
    if withdrawal.status != 'pending':
        flash("لا يمكن تعديل هذا الطلب لأن حالته ليست قيد الانتظار.", "warning")
        return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))
    
    try:
        # ✅ الحقول الجديدة من النموذج
        bank_name = request.form.get('bank_name', '').strip()
        transfer_company = request.form.get('transfer_company', '').strip()
        bank_reference = request.form.get('bank_reference', '').strip()
        admin_notes = request.form.get('admin_notes', '').strip()
        
        # 1. تحديث الحالة
        withdrawal.status = 'completed'
        withdrawal.updated_at = datetime.utcnow()
        withdrawal.notes = admin_notes if admin_notes else 'تمت الموافقة على السحب'
        
        # 2. تحديث رصيد المحفظة (خصم المبلغ)
        wallet.total_withdrawn += withdrawal.amount
        wallet.balance -= withdrawal.amount
        wallet.updated_at = datetime.utcnow()
        
        # 3. تسجيل حركة في المحفظة (Debit) مع بيانات التحويل
        generated_voucher = generate_unique_voucher_number()
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=withdrawal.amount,
            transaction_type='withdraw',
            voucher_number=generated_voucher,
            bank_reference=bank_reference if bank_reference else None,
            transfer_company=transfer_company if transfer_company else None,
            description=f"سحب رصيد - طلب رقم: {withdrawal.request_number}"
        )
        
        db.session.add(transaction)
        db.session.add(wallet)
        db.session.add(withdrawal)
        
        # 4. إنشاء حركة خزينة المنصة (TreasuryEntry) - إيداع للمنصة من حساب المورد
        treasury_entry = TreasuryEntry(
            reference_number=bank_reference if bank_reference else None,
            voucher_number=generated_voucher,
            entry_type='withdraw',  # أو 'debit'
            amount=withdrawal.amount,
            currency='SAR',
            owner_type='supplier',
            owner_id=withdrawal.supplier_id,
            description=f"سحب رصيد المورد - طلب رقم: {withdrawal.request_number}"
        )
        
        db.session.add(treasury_entry)
        db.session.commit()
        
        flash("تم اعتماد طلب السحب وخصم المبلغ من المحفظة بنجاح.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Withdrawal Approve Error: {e}")
        flash("حدث خطأ أثناء اعتماد الطلب.", "danger")
        
    return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))


# 3.4 رفض طلب السحب
@wallet_bp.route('/admin/withdrawals/<string:request_number>/reject', methods=['POST'])
@login_required
def reject_withdrawal(request_number):
    """رفض طلب السحب دون خصم المبلغ"""
    if session.get('user_type') not in ['admin', 'admin_staff']:
        abort(403)
        
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    
    if withdrawal.status != 'pending':
        flash("لا يمكن تعديل هذا الطلب لأن حالته ليست قيد الانتظار.", "warning")
        return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))
    
    try:
        withdrawal.status = 'rejected'
        withdrawal.updated_at = datetime.utcnow()
        
        db.session.add(withdrawal)
        db.session.commit()
        
        flash("تم رفض طلب السحب. المبلغ لم يتم خصمه من المحفظة.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Withdrawal Reject Error: {e}")
        flash("حدث خطأ أثناء رفض الطلب.", "danger")
        
    return redirect(url_for('wallet_app.admin_view_withdrawal', request_number=request_number))


# 4. مسار سند صرف مستحقات مالية للمورد
@wallet_bp.route('/supplier/wallet/receipt/<string:request_number>', methods=['GET'])
@login_required
def supplier_withdrawal_receipt(request_number):
    """عرض سند صرف مستحقات مالية للمورد"""
    if session.get('user_type') not in ['supplier', 'supplier_staff']:
        abort(403)
        
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    
    # التأكد أن المورد الحالي هو صاحب الطلب
    if withdrawal.supplier_id != current_user.id:
        abort(403)
        
    return render_template('suppliers/withdrawal_receipt.html', withdrawal=withdrawal)
