# coding: utf-8
# 📂 apps/admin_suppliers_wallets/routes/withdraw_requests_controller.py

from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.admin_suppliers_wallets.services.wallet_service import (
    get_withdraw_requests,
    update_withdrawal_status
)

# إنشاء الـ Blueprint مع تحديد الـ template_folder إذا لزم الأمر
bp = Blueprint('withdraw_requests_controller', __name__, template_folder='../templates')

PER_PAGE = 10


@bp.route('/withdraw-requests', methods=['GET'], endpoint='withdraw_requests_list')
@login_required
def withdraw_requests_list():
    """
    عرض صفحة طلبات السحب مع الفلترة والبحث والترقيم.
    """
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')
    search_query = request.args.get('q', '', type=str)

    result = get_withdraw_requests(
        status=status_filter,
        search=search_query,
        page=page,
        per_page=PER_PAGE
    )

    return render_template(
        'admin/withdraw_requests.html',
        withdrawals=result['items'],
        pagination=result['pagination'],
        status_filter=status_filter,
        search_query=search_query
    )


@bp.route('/withdraw-requests/<int:request_id>/action', methods=['POST'])
@login_required
def process_withdraw_request_post(request_id):
    """
    معالجة طلب السحب عبر POST (اعتماد أو رفض).
    """
    try:
        action = request.form.get('action')
        reason = request.form.get('reason', '')

        result = update_withdrawal_status(request_id, action, reason)

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'danger')

    except Exception as e:
        flash(f'حدث خطأ أثناء معالجة الطلب: {str(e)}', 'danger')

    # ✅ استخدام الاسم المركب الصحيح للـ Blueprint في التوجيه
    return redirect(url_for(
        'admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list',
        status=request.args.get('status', 'pending'),
        q=request.args.get('q', '')
    ))
