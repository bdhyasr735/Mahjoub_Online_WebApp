# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

from datetime import datetime
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

    avail_bal = 0.00
    min_withdraw = 50.00
    curr = 'SAR'

    if wallet_obj:
        avail_bal = float(getattr(wallet_obj, 'balance_sar', 0.00))
        curr = getattr(wallet_obj, 'default_currency', 'SAR')

    summary = {
        'available_balance': avail_bal,
        'min_withdraw_amount': min_withdraw,
        'currency': curr
    }

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method', 'bank')

            if not wallet_obj:
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك.", "danger")
            elif amount < min_withdraw:
                flash(f"الحد الأدنى للسحب هو {min_withdraw:,.2f} {curr}", "danger")
            elif amount > avail_bal:
                flash("المبلغ المطلوب يتجاوز الرصيد المتاح حالياً للسحب!", "danger")
            elif not registered_owner:
                flash("اسم المالك غير مسجل في قاعدة البيانات.", "danger")
            else:
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                details_text = f" - التفاصيل: {registered_details}" if registered_details else ""
                
                new_tx = WalletTransaction(
                    wallet_id=wallet_obj.id,
                    owner_id=supplier_id,     
                    owner_type='supplier',   
                    trans_type='withdrawal',
                    status='pending',
                    amount=amount,
                    currency=curr,
                    description=f"طلب سحب عبر {payout_label} | المالك: {registered_owner}{details_text}",
                    payout_method=payout_label,
                    account_details=registered_details or 'مسجل بالنظام'
                )

                db.session.add(new_tx)
                db.session.commit()

                flash("تم تقديم طلب السحب بنجاح، وهو قيد المراجعة.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
        except ValueError:
            flash("يرجى إدخال مبلغ مالي صحيح.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ: {str(e)}", "danger")

    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)
    query = query.filter(WalletTransaction.trans_type == 'withdrawal')

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(WalletTransaction.id.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)

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
