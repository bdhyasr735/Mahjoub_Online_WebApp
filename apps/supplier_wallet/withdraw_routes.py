# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

import uuid
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet import wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_trx_type_attr, 
    get_status_attr,
    get_registered_supplier_payout_info
)

@wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    trx_type_col = get_trx_type_attr()
    status_col = get_status_attr()

    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    avail_bal = 0.00
    min_withdraw = 50.00
    curr = 'ر.س'

    if wallet_obj:
        avail_bal = getattr(wallet_obj, 'available_balance', None)
        if avail_bal is None:
            avail_bal = max(0.00, float(getattr(wallet_obj, 'balance_sar', 0.00)))
        curr = getattr(wallet_obj, 'currency', 'ر.س')

    summary = {
        'available_balance': float(avail_bal),
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
                ref_code = f"WDR-{uuid.uuid4().hex[:6].upper()}"
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                details_text = f" - التفاصيل: {registered_details}" if registered_details else ""
                
                tx_kwargs = {
                    'wallet_id': wallet_obj.id,
                    'owner_id': supplier_id,      
                    'owner_type': 'supplier',    
                    'amount': amount,
                    'reference_number': ref_code, 
                    'description': f"طلب سحب عبر {payout_label} | المالك: {registered_owner}{details_text}",
                    'created_at': datetime.utcnow()
                }

                if status_col is not None and hasattr(WalletTransaction, 'status'):
                    tx_kwargs['status'] = 'pending'

                for field, val in [('payout_method', payout_label), ('account_details', registered_details or 'مسجل بالنظام'), ('owner_name', registered_owner)]:
                    if hasattr(WalletTransaction, field):
                        tx_kwargs[field] = val

                for col_name in ['trans_type', 'transaction_type', 'trx_type']:
                    if hasattr(WalletTransaction, col_name):
                        tx_kwargs[col_name] = 'withdrawal'
                        break

                db.session.add(WalletTransaction(**tx_kwargs))
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
    if trx_type_col is not None:
        query = query.filter(trx_type_col.in_(['withdrawal', 'debit']))

    if status_filter != 'all' and status_col is not None:
        query = query.filter(status_col == status_filter)

    pagination_obj = query.order_by(WalletTransaction.id.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    items = pagination_obj.items() if callable(pagination_obj.items) else pagination_obj.items

    pagination = {
        'items': list(items) if items else [],
        'page': pagination_obj.page,
        'total_pages': pagination_obj.pages,
        'total_items': pagination_obj.total,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'per_page': PER_PAGE
    }

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        wallet=summary,
        withdrawals=pagination['items'],
        active_filter=status_filter,
        pagination_obj=pagination_obj,
        pagination=pagination,
        registered_owner=registered_owner,
        registered_details=registered_details
    )
