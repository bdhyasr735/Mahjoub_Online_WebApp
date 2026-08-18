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

# ✅ استيراد قوائم البنوك والشركات المالية لتمريرها للواجهة (Modal)
try:
    from apps.data.yemen_banks import yemen_banks
except ImportError:
    yemen_banks = []

try:
    from apps.data.financial_companies import financial_companies
except ImportError:
    financial_companies = []

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
        search_query=search_query,
        yemen_banks=yemen_banks,                 # ✅ تمرير قائمة البنوك
        financial_companies=financial_companies  # ✅ تمرير قائمة الشركات المالية
    )


@bp.route('/withdraw-requests/<int:request_id>/action', methods=['POST'])
@login_required
def process_withdraw_request_post(request_id):
    """
    معالجة طلب السحب عبر POST (اعتماد أو رفض) مع التقاط بيانات التوثيق المالي.
    """
    try:
        action = request.form.get('action')
        reason = request.form.get('reason', '')
        
        # ✅ التقاط بيانات التوثيق المالي الجديدة من الـ Modal
        transfer_number = request.form.get('transfer_number')
        approval_ref = request.form.get('approval_ref')
        payout_bank = request.form.get('payout_bank')

        # تمرير البيانات المضافة إلى خدمة التحديث
        result = update_withdrawal_status(
            request_id=request_id,
            action=action,
            reason=reason,
            transfer_number=transfer_number,
            approval_ref=approval_ref,
            payout_bank=payout_bank
        )

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
