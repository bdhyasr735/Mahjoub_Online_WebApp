# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from decimal import Decimal
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id,
    get_or_create_supplier_wallet,
    get_registered_supplier_payout_info
)

@supplier_wallet_bp.route('/', methods=['GET'], strict_slashes=False)
@supplier_wallet_bp.route('/wallet', methods=['GET'], strict_slashes=False)
@login_required
def wallet_dashboard():
    """عرض كشف الحساب المحاسبي الفعلي للمورد (الحركات المكتملة فقط) مع الفلترة الزمنية والنوعية."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    # الأرصدة والملخص المالي
    balance_sar = float(getattr(wallet_obj, 'balance_sar', 0.00)) if wallet_obj else 0.00
    total_withdrawn = float(getattr(wallet_obj, 'total_withdrawn', 0.00)) if wallet_obj else 0.00
    curr = getattr(wallet_obj, 'default_currency', 'SAR') if wallet_obj else 'SAR'

    summary = {
        'balance_sar': balance_sar,
        'available_balance': balance_sar,
        'total_withdrawn': total_withdrawn,
        'currency': curr
    }

    # 1. إعدادات التقسيم (Pagination)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 2. استقبال متغيرات الفلترة من الـ UI (النوع، البحث، والسنة، والشهر)
    type_filter = request.args.get('type', '')
    search_query = request.args.get('search', '').strip()
    year_filter = request.args.get('year', type=int)
    month_filter = request.args.get('month', type=int)

    # 3. تعريف مصفوفات أنواع الحركات للفلترة الذكية
    credit_types = ['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit']
    debit_types = ['debit', 'withdrawal', 'commission_deduction', 'adjustment_debit']

    # 4. بناء الاستعلام الأساسي (المكتملة فقط)
    query = WalletTransaction.query.filter_by(
        wallet_id=wallet_obj.id if wallet_obj else -1,
        status='completed'
    )

    # 5. تطبيق فلتر النوع (Type)
    if type_filter == 'credit':
        query = query.filter(WalletTransaction.trans_type.in_(credit_types))
    elif type_filter == 'debit':
        query = query.filter(WalletTransaction.trans_type.in_(debit_types))

    # 6. تطبيق فلتر البحث المباشر
    if search_query:
        query = query.filter(
            db.or_(
                WalletTransaction.reference_number.ilike(f"%{search_query}%"),
                WalletTransaction.voucher_number.ilike(f"%{search_query}%"),
                WalletTransaction.description.ilike(f"%{search_query}%")
            )
        )

    # 7. تطبيق الفلاتر الزمنية (السنة والشهر) بدقة على حقل الإنشاء
    if year_filter:
        query = query.filter(db.extract('year', WalletTransaction.created_at) == year_filter)
    if month_filter:
        query = query.filter(db.extract('month', WalletTransaction.created_at) == month_filter)

    # 8. التنفيذ والترتيب
    pagination_obj = query.order_by(
        WalletTransaction.created_at.desc(), 
        WalletTransaction.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'supplier_wallet/wallet.html',
        wallet=wallet_obj,
        summary=summary,
        transactions=pagination_obj.items,
        pagination=pagination_obj,
        active_type=type_filter,
        search_query=search_query,
        active_year=year_filter,
        active_month=month_filter,
        registered_owner=registered_owner,
        registered_details=registered_details
    )


@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    """معالجة عرض صفحة طلب السحب واستقبال بيانات الإرسال للمورد."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    # الأرصدة والملخص المالي لصفحة السحب
    balance_sar = float(getattr(wallet_obj, 'balance_sar', 0.00)) if wallet_obj else 0.00
    total_withdrawn = float(getattr(wallet_obj, 'total_withdrawn', 0.00)) if wallet_obj else 0.00
    curr = getattr(wallet_obj, 'default_currency', 'SAR') if wallet_obj else 'SAR'

    summary = {
        'balance_sar': balance_sar,
        'available_balance': balance_sar,
        'total_withdrawn': total_withdrawn,
        'currency': curr,
        'min_withdraw_amount': 50.0
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0.00))
            payout_method = request.form.get('payout_method', 'bank_transfer')
            min_withdraw = summary['min_withdraw_amount']

            # 1. التحقق من صحة المبلغ والمحفظة
            if amount < min_withdraw:
                flash(f"عذراً، الحد الأدنى لطلب السحب هو {min_withdraw} ر.س.", "danger")
                return redirect(url_for('supplier_wallet.withdraw'))

            if amount > balance_sar:
                flash("عذراً، الرصيد المتاح لا يكفي لتغطية مبلغ السحب المطلوب.", "danger")
                return redirect(url_for('supplier_wallet.withdraw'))

            # 2. إنشاء حركة السحب بحالة معلقة (pending)
            new_withdrawal = WalletTransaction(
                wallet_id=wallet_obj.id,
                owner_type='supplier',
                owner_id=supplier_id,
                trans_type='withdrawal',
                status='pending',
                amount=amount,
                currency=curr,
                reference_number=None,  
                voucher_number=None,    
                description=f"طلب سحب مبيعات عبر ({payout_method}) - قيد المراجعة والاعتماد"
            )

            db.session.add(new_withdrawal)
            db.session.commit()

            # 3. إظهار التنبيه النظيف والمباشر بدون أرقام
            flash("تم تقديم طلب السحب بنجاح، وهو قيد المراجعة والاعتماد.", "success")
            return redirect(url_for('supplier_wallet.wallet_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء تقديم طلب السحب: {str(e)}", "danger")
            return redirect(url_for('supplier_wallet.withdraw'))

    # جلب طلبات السحب الخاصة بالصفحة لتفادي أي أخطاء في عرض الجدول أو الباجينيشن
    page = request.args.get('page', 1, type=int)
    pagination_obj = WalletTransaction.query.filter_by(
        wallet_id=wallet_obj.id if wallet_obj else -1,
        trans_type='withdrawal'
    ).order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    # في حال كان الطلب GET، يتم عرض صفحة نموذج طلب السحب مع كامل المتغيرات اللازمة
    return render_template(
        'supplier_wallet/withdraw.html',
        wallet=wallet_obj,
        summary=summary,
        pagination=pagination_obj,
        transactions=pagination_obj.items,
        registered_owner=registered_owner,
        registered_details=registered_details
    )


@supplier_wallet_bp.route('/export-pdf', methods=['GET'], strict_slashes=False)
@login_required
def export_wallet_pdf():
    """مسار تصدير كشف حساب المحفظة بصيغة PDF (معالج لتجنب خطأ BuildError)."""
    try:
        flash("جاري تجهيز ملف الـ PDF الخاص بك...", "info")
        return redirect(url_for('supplier_wallet.wallet_dashboard'))
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير ملف الـ PDF: {str(e)}", "danger")
        return redirect(url_for('supplier_wallet.wallet_dashboard'))