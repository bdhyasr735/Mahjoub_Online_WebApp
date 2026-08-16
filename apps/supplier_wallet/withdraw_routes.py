# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_registered_supplier_payout_info,
    generate_transaction_ref  # تم استيراد دالة التوليد المجهزة
)

MIN_WITHDRAW_AMOUNT = Decimal('50.00')

@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False, endpoint='submit_withdrawal')
@login_required
def submit_withdrawal():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    registered_owner, registered_details = get_registered_supplier_payout_info(supplier_id)

    avail_bal = Decimal('0.00')
    curr = 'SAR'

    if wallet_obj:
        avail_bal = Decimal(str(getattr(wallet_obj, 'balance_sar', '0.00')))
        curr = getattr(wallet_obj, 'default_currency', 'SAR')

    summary = {
        'available_balance': float(avail_bal),
        'balance_sar': float(avail_bal),
        'min_withdraw_amount': float(MIN_WITHDRAW_AMOUNT),
        'currency': curr
    }

    # معالجة إرسال طلب السحب (POST)
    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip()
            amount = Decimal(str(raw_amount))
            method = request.form.get('method', 'bank')

            if not wallet_obj:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "message": "تعذر الوصول إلى حساب المحفظة الخاص بك."}), 400
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك.", "danger")
                return redirect(url_for('supplier_wallet.submit_withdrawal'))

            # 🔒 [Pessimistic Locking]
            locked_wallet = db.session.query(SupplierWallet)\
                .options(lazyload(SupplierWallet.supplier))\
                .filter(SupplierWallet.id == wallet_obj.id)\
                .with_for_update()\
                .first()

            if not locked_wallet:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "message": "تعذر تأمين حساب المحفظة، يرجى المحاولة لاحقاً."}), 400
                flash("تعذر تأمين حساب المحفظة، يرجى المحاولة لاحقاً.", "danger")
                return redirect(url_for('supplier_wallet.submit_withdrawal'))

            real_avail_bal = Decimal(str(getattr(locked_wallet, 'balance_sar', '0.00')))

            error_msg = None
            if real_avail_bal <= Decimal('0.00'):
                error_msg = "رصيدك غير كافٍ، لا يوجد رصيد متاح للسحب حالياً."
            elif amount > real_avail_bal:
                error_msg = "رصيدك غير كافٍ لتغطية المبلغ المطلوب!"
            elif amount < MIN_WITHDRAW_AMOUNT:
                error_msg = f"الحد الأدنى لطلب السحب هو {float(MIN_WITHDRAW_AMOUNT):,.2f} {curr}"

            if error_msg:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "message": error_msg}), 400
                flash(error_msg, "danger")
            else:
                owner_name = registered_owner or f"مورد رقم #{supplier_id}"
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                details_text = f" | التفاصيل: {registered_details}" if registered_details else ""
                full_desc = f"طلب سحب عبر {payout_label} | المالك: {owner_name}{details_text}"[:255]

                # جلب كود المورد لتوليد رقم مرجعي فريد وآمن عبر الدالة المجهزة
                sup_code = f"SUP{supplier_id}"
                if locked_wallet.supplier and hasattr(locked_wallet.supplier, 'supplier_code'):
                    sup_code = locked_wallet.supplier.supplier_code or sup_code

                ref_num, vch_num = generate_transaction_ref(locked_wallet.id, sup_code, prefix='WTH')

                # ✅ إنشاء الحركة بالرقم المرجعي ورقم السند المولدان تلقائياً
                new_tx = WalletTransaction(
                    wallet_id=locked_wallet.id,
                    trans_type='withdrawal',
                    status='pending',
                    amount=amount,
                    currency=curr,
                    reference_number=ref_num,
                    voucher_number=vch_num,
                    description=full_desc
                )

                db.session.add(new_tx)
                db.session.commit()

                # ⚡ [ZSA Response Handling] استجابة فورية متزامنة
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        "status": "success",
                        "message": "تم تقديم طلب السحب بنجاح، وهو قيد المراجعة والاعتماد.",
                        "new_balance": float(real_avail_bal),
                        "reference_number": ref_num,
                        "voucher_number": vch_num
                    })

                flash("تم تقديم طلب السحب بنجاح، وهو قيد المراجعة والاعتماد.", "success")
                return redirect(url_for('supplier_wallet.submit_withdrawal'))
                
        except (ValueError, InvalidOperation):
            db.session.rollback()
            err = "يرجى إدخال مبلغ مالي صحيح."
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": err}), 400
            flash(err, "danger")
        except Exception as e:
            db.session.rollback()
            err = f"حدث خطأ غير متوقع أثناء حفظ الطلب: {str(e)}"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "error", "message": err}), 500
            flash(err, "danger")

    # استعلام واستعراض سجل عمليات السحب (GET)
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)
    query = query.filter(WalletTransaction.trans_type == 'withdrawal')

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        wallet=wallet_obj,
        withdrawals=pagination_obj.items,
        active_filter=status_filter,
        pagination=pagination_obj,
        registered_owner=registered_owner,
        registered_details=registered_details
    )
