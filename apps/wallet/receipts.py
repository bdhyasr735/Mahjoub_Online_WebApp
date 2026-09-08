# coding: utf-8
# 📂 apps/wallet/receipts.py - سند صرف مستحقات مالية للمورد

from flask import render_template, request, abort
from flask_login import login_required, current_user
from apps.models.wallet_db import WithdrawalRequest
from apps.wallet.routes import wallet_bp

@wallet_bp.route('/supplier/wallet/receipt/<string:request_number>', methods=['GET'])
@login_required
def supplier_withdrawal_receipt(request_number):
    """عرض سند صرف مستحقات مالية للمورد"""
    if session.get('user_type') not in ['supplier', 'supplier_staff']:
        abort(403)
        
    withdrawal = WithdrawalRequest.query.filter_by(request_number=request_number).first_or_404()
    
    # التأكد أن المورد الحالي أو موظف المورد هو صاحب الطلب
    if session.get('user_type') == 'supplier':
        if withdrawal.supplier_id != current_user.id:
            abort(403)
    elif session.get('user_type') == 'supplier_staff':
        if withdrawal.supplier_id != current_user.supplier_id:
            abort(403)
        
    return render_template('suppliers/withdrawal_receipt.html', withdrawal=withdrawal)
