# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_registered_supplier_payout_info
)

@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    avail_bal = Decimal('0.00')
    min_withdraw = Decimal('50.00')
    curr = 'SAR'

    if wallet_obj:
        avail_bal = Decimal(str(getattr(wallet_obj, 'balance_sar', '0.00')))
        curr = getattr(wallet_obj, 'default_currency', 'SAR')

    summary = {
        'available_balance': float(avail_bal),
        'min_withdraw_amount': float(min_withdraw),
        'currency': curr
    }

    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0')
            amount = Decimal(str(raw_amount))
            method = request.form.get('method', 'bank')

            # --- منطق التحقق والشروط ---
            if not wallet_obj:
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك.", "danger")
            elif avail_bal <= Decimal('0.00'):
                flash("رصيدك غير كافٍ، لا يوجد رصيد متاح للسحب حالياً.", "danger")
            elif amount > avail_bal:
                flash("رصيدك غير كافٍ لتغطية المبلغ المطلوب!", "danger")
            elif amount < min_withdraw:
                flash(f"الحد الأدنى للسحب هو {float(min_withdraw):,.2f} {curr}", "danger")
            else:
                # في حال عدم وجود اسم مالك مسجل، نستخدم اسم افتراضي لتفادي فشل الحفظ
                owner_name = registered_owner or f"مورد رقم #{supplier_id}"
                
                # توليد رقم مرجعي فريد لمنع خطأ الحفظ في قاعدة البيانات
                ref_num = f"WD-{uuid.uuid4().hex[:8].upper()}"

                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                details_text = f" - التفاصيل: {registered_details}" if registered_details else ""
                
                new_tx = WalletTransaction(
                    reference_number=ref_num,
                    wallet_id=wallet_obj.id,
                    owner_id=supplier_id,     
                    owner_type='supplier',   
                    trans_type='withdrawal',
                    status='pending',
                    amount=amount,
                    currency=curr,
                    description=f"طلب سحب عبر {payout_label} | المالك: {owner_name}{details_text}",
                    payout_method=payout_label,
                    account_details=registered_details or 'مسجل بالنظام',
                    created_by=supplier_id
                )

                db.session.add(new_tx)
                db.session.commit()

                flash("تم تقديم طلب السحب بنجاح، وهو قيد المراجعة.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
                
        except (ValueError, InvalidOperation):
            flash("يرجى إدخال مبلغ مالي صحيح.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ غير متوقع أثناء حفظ الطلب: {str(e)}", "danger")

    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)
    query = query.filter(WalletTransaction.trans_type == 'withdrawal')

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(
        WalletTransaction.created_at.desc(), 
        WalletTransaction.id.desc()
    ).paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        wallet=summary,
        withdrawals=pagination_obj.items,
        active_filter=status_filter,
        pagination=pagination_obj,
        registered_owner=registered_owner,
        registered_details=registered_details
    )
