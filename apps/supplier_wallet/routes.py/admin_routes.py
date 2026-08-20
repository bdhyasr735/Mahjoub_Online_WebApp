# coding: utf-8
"""
📂 apps/supplier_wallet/routes/admin_routes.py
متحكم الإدارة المالية للمنصة (Admin Approvals & Auditing)
- اعتماد وقبول طلبات السحب وصرف المبالغ بنكياً
- إطلاق إشعارات Toasts الفورية للموردين
"""

from flask import Blueprint, request, redirect, url_for, flash
from apps.extensions import db
from apps.models.wallet_db import WithdrawalRequest
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService

admin_wallet_bp = Blueprint('admin_wallet', __name__, url_prefix='/admin/financial')

@admin_wallet_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
def approve_request(request_id):
    """اعتماد طلب السحب وإصدار سند الصرف البنكي"""
    try:
        admin_name = request.form.get('admin_name', 'مكتب المراجعة المالية')
        transfer_number = request.form.get('transfer_number')
        notes = request.form.get('notes', 'تم التحويل البنكي الفوري بنجاح')

        tx = WalletService.approve_withdrawal(
            session=db.session,
            request_id=request_id,
            admin_name=admin_name,
            transfer_number=transfer_number,
            notes=notes
        )
        db.session.commit()

        # إشعار فوري بنجاح الصرف
        NotificationService.notify_withdrawal_approved(float(abs(tx.amount)), tx.voucher_number)
        flash('تم اعتماد طلب السحب وإصدار السند بنجاح.', 'success')

    except Exception as e:
        db.session.rollback()
        NotificationService.notify_error(f"خطأ أثناء اعتماد الطلب: {str(e)}")
        flash(f'حدث خطأ أثناء اعتماد الطلب: {str(e)}', 'error')

    return redirect(request.referrer or url_for('supplier_wallet.wallet_dashboard'))
