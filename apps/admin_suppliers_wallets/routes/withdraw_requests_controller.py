# coding: utf-8
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.admin_suppliers_wallets.routes.suppliers_wallets_controller import bp
from apps.admin_suppliers_wallets.services.wallet_service import (
    get_withdraw_requests,
    update_withdrawal_status
)

PER_PAGE = 10


@bp.route('/withdraw-requests', methods=['GET'], endpoint='withdraw_requests_list')
@login_required
def withdraw_requests_list():
    """
    عرض صفحة طلبات السحب مع الفلترة والبحث والترقيم.
    """
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')  # افتراضي: المعلقة
    search_query = request.args.get('q', '', type=str)

    # استدعاء الخدمة لجلب الطلبات
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

        # استدعاء الخدمة لتحديث الحالة
        result = update_withdrawal_status(request_id, action, reason)

        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'danger')

    except Exception as e:
        flash(f'حدث خطأ أثناء معالجة الطلب: {str(e)}', 'danger')

    # إعادة التوجيه إلى صفحة الطلبات مع الحفاظ على الفلاتر الحالية
    return redirect(url_for(
        '.withdraw_requests_list',
        status=request.args.get('status', 'pending'),
        q=request.args.get('q', '')
    ))
