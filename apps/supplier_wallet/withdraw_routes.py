# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from sqlalchemy.orm import noload
from apps.extensions import db, limiter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_registered_supplier_payout_info,
    generate_transaction_ref  # تم استيرادها لاستخدامها في المرجع
)

MIN_WITHDRAW_AMOUNT = Decimal('50.00')

@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False, endpoint='submit_withdrawal')
@login_required
@limiter.exempt  
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
        'min_withdraw_amount': float(MIN_WITHDRAW_AMOUNT),
        'currency': curr
    }

    if request.method == 'POST':
        try:
            raw_amount = request.form.get('amount', '0').strip()
            amount = Decimal(str(raw_amount))
            method = request.form.get('payout_method', 'bank_transfer')

            if not supplier_id:
                return jsonify({"status": "error", "code": "SUPPLIER_NOT_FOUND", "message": "تعذر معرفة هوية المورد."}), 400

            # 🔒 Locking
            locked_wallet = db.session.query(SupplierWallet)\
                .options(noload('*'))\
                .filter(SupplierWallet.supplier_id == supplier_id)\
                .with_for_update()\
                .first()

            if not locked_wallet:
                return jsonify({"status": "error", "message": "المحفظة غير مهيأة بعد."}), 400

            # 🛑 منع تعدد الطلبات
            existing_pending = db.session.query(WalletTransaction)\
                .filter(WalletTransaction.wallet_id == locked_wallet.id)\
                .filter(WalletTransaction.trans_type == 'withdrawal')\
                .filter(WalletTransaction.status == 'pending')\
                .first()

            if existing_pending:
                return jsonify({"status": "warning", "code": "PENDING_REQUEST_EXISTS", "message": "لديك طلب سحب قيد المراجعة حالياً."}), 409

            real_avail_bal = Decimal(str(getattr(locked_wallet, 'balance_sar', '0.00')))

            # التحقق المالي
            if amount > real_avail_bal:
                return jsonify({"status": "error", "message": "المبلغ المطلوب يتجاوز الرصيد المتاح."}), 400
            if amount < MIN_WITHDRAW_AMOUNT:
                return jsonify({"status": "error", "message": f"الحد الأدنى للسحب هو {float(MIN_WITHDRAW_AMOUNT):,.2f} {curr}"}), 400

            # ⚙️ إنشاء المراجع الموحدة
            sup_code = locked_wallet.wallet_code.split('-')[-1] if locked_wallet.wallet_code else f"S{supplier_id}"
            ref, vch = generate_transaction_ref(locked_wallet.id, sup_code, prefix='WTH')

            new_tx = WalletTransaction(
                wallet_id=locked_wallet.id,
                trans_type='withdrawal',
                status='pending',
                amount=amount,
                currency=curr,
                description=f"طلب سحب | {registered_owner or 'مورد'} | {method}",
                reference_number=ref,
                voucher_number=vch
            )

            db.session.add(new_tx)
            db.session.commit()

            return jsonify({
                "status": "success", 
                "message": "تم تقديم طلب السحب بنجاح.",
                "data": {"tx_id": new_tx.id, "ref": ref}
            }), 201
                
        except (ValueError, InvalidOperation):
            db.session.rollback()
            return jsonify({"status": "error", "message": "القيمة المالية المدخلة غير صحيحة."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"خطأ داخلي: {str(e)}"}), 500

    # GET Request
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)\
                                   .filter(WalletTransaction.trans_type == 'withdrawal')

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'supplier_wallet/withdraw.html',
        summary=summary,
        transactions=pagination_obj.items,
        pagination=pagination_obj,
        active_filter=status_filter
    )
