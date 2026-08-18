# coding: utf-8
# 📂 apps/admin_suppliers_wallets/controllers/withdraw_requests_controller.py

from flask import render_template, request, redirect, url_for, flash
from apps.admin_suppliers_wallets.services import wallet_service

def withdraw_requests_list():
    """عرض قائمة طلبات السحب مع دعم الفلترة والبحث"""
    status = request.args.get('status', 'pending')
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # التقاط الـ ID الحقيقي لتمريره للـ Modal
    req_id = request.args.get('req_id')
    modal_trigger = request.args.get('modal')
    
    data = wallet_service.get_withdraw_requests(status=status, search=search, page=page)
    
    return render_template(
        'admin_suppliers_wallets/withdraw_requests.html',
        data=data,
        status=status,
        search=search,
        req_id=req_id,
        modal_trigger=modal_trigger
    )

def process_withdraw_request_post():
    """معالجة طلبات السحب (اعتماد أو رفض)"""
    request_id = request.form.get('request_id')
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    transfer_number = request.form.get('transfer_number')
    approval_ref = request.form.get('approval_ref')
    payout_bank = request.form.get('payout_bank')

    result = wallet_service.update_withdrawal_status(
        request_id=request_id,
        action=action,
        reason=reason,
        transfer_number=transfer_number,
        approval_ref=approval_ref,
        payout_bank=payout_bank
    )

    if result['success']:
        flash(result['message'], 'success')
        # الحصول على المعرف الحقيقي من قاعدة البيانات
        actual_id = result.get('actual_id', request_id)
        
        # التوجيه إلى المسار المحدد بالـ Blueprint (withdraw_requests)
        if action == 'approve':
            return redirect(url_for(
                'withdraw_requests.withdraw_requests_list',
                status=request.args.get('status', 'pending'),
                modal='success',
                req_id=actual_id
            ))
        else:
            return redirect(url_for(
                'withdraw_requests.withdraw_requests_list', 
                status=request.args.get('status', 'pending')
            ))
    else:
        flash(result['message'], 'danger')
        return redirect(url_for('withdraw_requests.withdraw_requests_list')