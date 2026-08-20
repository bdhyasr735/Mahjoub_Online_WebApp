# coding: utf-8
"""
📂 apps/supplier_wallet/routes/admin_routes.py
متحكم الإدارة المالية للمنصة (Admin Approvals & Auditing)
- اعتماد وقبول/رفض طلبات السحب وصرف المبالغ بنكياً
- إطلاق إشعارات Toasts الفورية للموردين
"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user
from apps.extensions import db
from apps.models.wallet_db import WithdrawalRequest
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService

admin_wallet_bp = Blueprint('admin_wallet', __name__, url_prefix='/admin/financial')


@admin_wallet_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
def approve_request(request_id):
    """اعتماد طلب السحب وإصدار سند الصرف البنكي"""
    try:
        # جلب اسم المشرف الحالي تلقائياً من المستخدم المسجل أو من النموذج
        default_admin = getattr(current_user, 'name', getattr(current_user, 'username', 'مكتب المراجعة المالية'))
        admin_name = request.form.get('admin_name') or default_admin
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


@admin_wallet_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
def reject_request(request_id):
    """رفض طلب السحب وإعادة المبلغ المحجوز إلى حساب المورد"""
    try:
        default_admin = getattr(current_user, 'name', getattr(current_user, 'username', 'مكتب المراجعة المالية'))
        admin_name = request.form.get('admin_name') or default_admin
        reason = request.form.get('reason', 'تم رفض طلب السحب من قبل الإدارة المالية')

        wdr = WalletService.reject_withdrawal(
            session=db.session,
            request_id=request_id,
            admin_name=admin_name,
            reason=reason
        )
        db.session.commit()

        flash('تم رفض طلب السحب وإعادة المبلغ إلى محفظة المورد.', 'warning')

    except Exception as e:
        db.session.rollback()
        NotificationService.notify_error(f"خطأ أثناء رفض الطلب: {str(e)}")
        flash(f'حدث خطأ أثناء رفض الطلب: {str(e)}', 'error')

    return redirect(request.referrer or url_for('supplier_wallet.wallet_dashboard'))
