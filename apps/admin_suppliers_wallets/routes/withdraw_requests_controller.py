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

# ✅ استيراد قائمة البنوك باستخدام الاسم الصحيح YEMEN_BANKS المعرف في ملف yemen_banks.py
try:
    from apps.data.yemen_banks import YEMEN_BANKS as yemen_banks
except ImportError:
    yemen_banks = []

try:
    from apps.data.financial_companies import FINANCIAL_COMPANIES as financial_companies
except ImportError:
    financial_companies = []

# إنشاء الـ Blueprint مع تحديد الـ template_folder إذا لزم الأمر
bp = Blueprint('withdraw_requests_controller', __name__, template_folder='../templates')

PER_PAGE = 10


@bp.route('/withdraw-requests', methods=['GET'], endpoint='withdraw_requests_list')
@login_required
def withdraw_requests_list():
    """
    عرض صفحة طلبات السحب مع الفلترة والبحث اللحظي والترقيم الديناميكي وحساب الإجمالي والعدد.
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

    items = result.get('items', [])
    
    # ✅ حساب إجمالي المبالغ للطلبات الظاهرة في القائمة الحالية
    total_withdraw_amount = sum(float(item.amount) for item in items if item.amount)
    
    # ✅ استخراج العدد الإجمالي للطلبات بشكل دقيق وآمن
    pagination_data = result.get('pagination', {})
    if isinstance(pagination_data, dict):
        total_count = pagination_data.get('total', len(items))
    else:
        total_count = getattr(pagination_data, 'total', len(items))
    
    if not total_count:
        total_count = len(items)

    # ✅ دعم البحث اللحظي عبر AJAX: إرجاع مكون الجدول فقط مع الحفاظ على تمرير البيانات لمنع أخطاء القوالب
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'admin/components/withdraw_requests_table.html',
            withdrawals=items,
            pagination=pagination_data,
            status_filter=status_filter,
            search_query=search_query,
            yemen_banks=yemen_banks,
            financial_companies=financial_companies
        )

    return render_template(
        'admin/withdraw_requests.html',
        withdrawals=items,
        pagination=pagination_data,
        total_withdraw_amount=total_withdraw_amount,  # ✅ تمرير إجمالي المبالغ للقالب
        total_count=total_count,                      # ✅ تمرير إجمالي عدد الطلبات للقالب
        status_filter=status_filter,
        search_query=search_query,
        yemen_banks=yemen_banks,                      # ✅ تمرير قائمة البنوك
        financial_companies=financial_companies       # ✅ تمرير قائمة الشركات المالية
    )


@bp.route('/withdraw-requests/<int:request_id>/action', methods=['POST'])
@login_required
def process_withdraw_request_post(request_id):
    """
    معالجة طلب السحب عبر POST (اعتماد أو رفض) مع التقاط بيانات التوثيق المالي.
    """
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    # ✅ التقاط بيانات التوثيق المالي الجديدة من الـ Modal
    transfer_number = request.form.get('transfer_number')
    approval_ref = request.form.get('approval_ref')
    payout_bank = request.form.get('payout_bank')

    try:
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
            
            # ✅ إذا كان الإجراء اعتماد، نقوم بتمرير بيانات الحوالة لعرض نافذة النجاح والنسخ
            if action == 'approve':
                return redirect(url_for(
                    'admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list',
                    page=request.args.get('page', 1, type=int),
                    status=request.args.get('status', 'pending'),
                    q=request.args.get('q', ''),
                    modal='success',
                    bank=payout_bank,
                    tnum=transfer_number
                ))
        else:
            flash(result['message'], 'danger')

    except Exception as e:
        flash(f'حدث خطأ أثناء معالجة الطلب: {str(e)}', 'danger')

    # ✅ الحفاظ على رقم الصفحة الحالية والبحث والفلترة عند إعادة التوجيه (الترقيم الديناميكي)
    return redirect(url_for(
        'admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list',
        page=request.args.get('page', 1, type=int),
        status=request.args.get('status', 'pending'),
        q=request.args.get('q', '')
    ))
