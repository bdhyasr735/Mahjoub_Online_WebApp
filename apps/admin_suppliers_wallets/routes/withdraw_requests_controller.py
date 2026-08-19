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
        total_withdraw_amount=total_withdraw_amount,    # ✅ تمرير إجمالي المبالغ للقالب
        total_count=total_count,                        # ✅ تمرير إجمالي عدد الطلبات للقالب
        status_filter=status_filter,
        search_query=search_query,
        yemen_banks=yemen_banks,                        # ✅ تمرير قائمة البنوك
        financial_companies=financial_companies         # ✅ تمرير قائمة الشركات المالية
    )


@bp.route('/withdraw-requests/<int:request_id>/action', methods=['POST'])
@login_required
def process_withdraw_request_post(request_id):
    """
    معالجة طلب السحب عبر POST (اعتماد أو رفض) مع التقاط بيانات التوثيق المالي والمعرف الحقيقي وتسجيلها في الخزينة.
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

        if result.get('success', False):
            # ✅ جلب رقم السند الحقيقي حصرياً من حقل voucher_number المطابق للجدول (مثل VCH-CK08WU)
            tx_obj = WalletTransaction.query.get(request_id)
            actual_code = getattr(tx_obj, 'voucher_number', None) or result.get('voucher_number') or f"VCH-{request_id}"
            
            # ✅ صياغة نص رسالة إشعار دقيقة ومخصصة بناءً على نوع الإجراء (اعتماد أم رفض) باستخدام الكود الصحيح
            if action == 'approve':
                bank_info = f" عبر ({payout_bank})" if payout_bank else ""
                trans_info = f" برقم حوالة: ({transfer_number})" if transfer_number else ""
                default_msg = f"تم اعتماد طلب السحب رقم ({actual_code}){bank_info}{trans_info} بنجاح وإرسال الإشعار للمورد."
                
                # 🔴 [إضافة جذرية للربط مع الخزينة]: تسجيل الحركة في جدول الخزينة مباشرة عند الاعتماد الناجح
                try:
                    from apps.models.treasury_db import TreasuryEntry
                    from datetime import datetime
                    
                    # التحقق من عدم تكرار السجل مسبقاً بنفس رقم المرجع
                    existing_entry = TreasuryEntry.query.filter_by(reference_number=actual_code).first()
                    if not existing_entry and tx_obj:
                        treasury_entry = TreasuryEntry(
                            reference_number=actual_code,
                            amount=getattr(tx_obj, 'amount', 0),
                            entry_type='expense',
                            description=f"صرف طلب سحب للمورد - سند رقم {actual_code}{bank_info}{trans_info}",
                            date=datetime.utcnow()
                        )
                        db.session.add(treasury_entry)
                        db.session.commit()
                except Exception as treasury_err:
                    print(f"❌ [Treasury Integration Error]: {str(treasury_err)}")

            elif action == 'reject':
                reason_info = f" بسبب: ({reason})" if reason else ""
                default_msg = f"تم رفض طلب السحب رقم ({actual_code}){reason_info} وإشعار المورد بذلك."
            else:
                default_msg = result.get('message', 'تمت العملية بنجاح وإرسال الإشعار للمورد.')

            flash(default_msg, 'success')
            
            # ✅ إعادة التوجيه مع تمرير معامل النجاح لفتح نافذة النجاح المنبثقة تلقائياً
            return redirect(url_for(
                'admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list',
                page=request.args.get('page', 1, type=int),
                status=request.args.get('status', 'pending'),
                q=request.args.get('q', ''),
                modal='success'
            ))
        else:
            flash(result.get('message', 'فشل تنفيذ العملية'), 'danger')

    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء معالجة الطلب: {str(e)}', 'danger')

    # ✅ الحفاظ على رقم الصفحة الحالية والبحث والفلترة عند حدوث خطأ أو فشل
    return redirect(url_for(
        'admin_suppliers_wallets.withdraw_requests_controller.withdraw_requests_list',
        page=request.args.get('page', 1, type=int),
        status=request.args.get('status', 'pending'),
        q=request.args.get('q', '')
    ))
