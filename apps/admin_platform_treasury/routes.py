# coding: utf-8
# 📂 apps/admin_platform_treasury/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.treasury_db import WithdrawalRequest
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from datetime import datetime

treasury_bp = Blueprint('treasury', __name__, template_folder='templates')

@treasury_bp.route('/admin/treasury/withdrawals', methods=['GET'])
@login_required
def list_withdrawals():
    """عرض قائمة طلبات السحب."""
    requests = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
    return render_template('admin/treasury/withdrawals.html', requests=requests)

@treasury_bp.route('/admin/treasury/approve/<int:req_id>', methods=['POST'])
@login_required
def approve_withdrawal(req_id):
    """الموافقة على السحب وتحديث المحفظة وسجل الحركات."""
    req = WithdrawalRequest.query.get_or_404(req_id)
    
    if req.status != 'pending':
        flash('هذا الطلب تمت معالجته مسبقاً', 'danger')
        return redirect(url_for('treasury.list_withdrawals'))

    try:
        wallet = SupplierWallet.query.filter_by(supplier_id=req.supplier_id).first()
        
        # التحقق من الرصيد
        if req.currency == 'YER' and wallet.balance_yer < req.amount:
            flash('رصيد المورد غير كافٍ', 'danger')
            return redirect(url_for('treasury.list_withdrawals'))

        # تحديث أرصدة المحفظة
        wallet.balance_yer -= req.amount
        wallet.total_withdrawn += req.amount
        
        # تسجيل الحركة المالية
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            trans_type='withdrawal',
            amount=-req.amount,
            currency=req.currency,
            balance_before=wallet.balance_yer + req.amount,
            balance_after=wallet.balance_yer,
            description=f"سحب أرباح طلب رقم: {req.id}",
            reference_number=f"WD-{req.id}"
        )
        
        req.status = 'approved'
        req.processed_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        flash('تمت الموافقة على السحب بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ أثناء معالجة العملية: {str(e)}', 'danger')
        
    return redirect(url_for('treasury.list_withdrawals'))

@treasury_bp.route('/admin/treasury/reject/<int:req_id>', methods=['POST'])
@login_required
def reject_withdrawal(req_id):
    """رفض طلب السحب مع حفظ سبب الرفض مشفراً."""
    req = WithdrawalRequest.query.get_or_404(req_id)
    reason = request.form.get('reason', 'لا يوجد سبب محدد')
    
    if req.status != 'pending':
        flash('لا يمكن رفض طلب تمت معالجته مسبقاً', 'danger')
        return redirect(url_for('treasury.list_withdrawals'))

    try:
        req.status = 'rejected'
        req.processed_at = datetime.utcnow()
        # يتم تشفير السبب تلقائياً عبر الـ setter في الموديل
        req.details = f"سبب الرفض: {reason}"
        
        db.session.commit()
        flash('تم رفض الطلب بنجاح', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ أثناء معالجة الرفض: {str(e)}', 'danger')
        
    return redirect(url_for('treasury.list_withdrawals'))
