# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.extensions import db, limiter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_registered_supplier_payout_info
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

            if not wallet_obj:
                return jsonify({"status": "error", "code": "WALLET_NOT_FOUND", "message": "تعذر الوصول إلى حساب المحفظة."}), 400

            # 🔒 [Pessimistic Locking]
            locked_wallet = db.session.query(SupplierWallet)\
                .filter(SupplierWallet.id == wallet_obj.id)\
                .with_for_update()\
                .first()

            # 🛑 [Professional Gate] منع تعدد الطلبات المعلقة
            existing_pending = db.session.query(WalletTransaction)\
                .filter(WalletTransaction.wallet_id == locked_wallet.id)\
                .filter(WalletTransaction.trans_type == 'withdrawal')\
                .filter(WalletTransaction.status == 'pending')\
                .first()

            if existing_pending:
                return jsonify({
                    "status": "warning", 
                    "code": "PENDING_REQUEST_EXISTS", 
                    "message": "لديك طلب سحب قيد المراجعة حالياً. يرجى الانتظار حتى يتم إتمام الطلب الحالي."
                }), 409

            real_avail_bal = Decimal(str(getattr(locked_wallet, 'balance_sar', '0.00')))

            # التحقق من القيود المالية
            if real_avail_bal <= Decimal('0.00'):
                return jsonify({"status": "error", "message": "رصيدك الحالي لا يسمح بالسحب."}), 400
            if amount > real_avail_bal:
                return jsonify({"status": "error", "message": "المبلغ المطلوب يتجاوز الرصيد المتاح."}), 400
            if amount < MIN_WITHDRAW_AMOUNT:
                return jsonify({"status": "error", "message": f"الحد الأدنى للسحب هو {float(MIN_WITHDRAW_AMOUNT):,.2f} {curr}"}), 400

            # إنشاء طلب السحب
            owner_name = registered_owner or f"مورد #{supplier_id}"
            full_desc = f"طلب سحب | {owner_name} | وسيلة: {method}"[:255]

            new_tx = WalletTransaction(
                wallet_id=locked_wallet.id,
                trans_type='withdrawal',
                status='pending',
                amount=amount,
                currency=curr,
                description=full_desc
            )

            db.session.add(new_tx)
            db.session.commit()

            return jsonify({
                "status": "success", 
                "message": "تم تقديم طلب السحب بنجاح. سيقوم فريقنا بمراجعته قريباً.",
                "data": {"tx_id": new_tx.id}
            }), 201
                
        except (ValueError, InvalidOperation):
            db.session.rollback()
            return jsonify({"status": "error", "message": "القيمة المالية المدخلة غير صحيحة."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": "حدث خطأ داخلي أثناء المعالجة."}), 500

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
        withdrawals=pagination_obj.items,
        pagination=pagination_obj,
        active_filter=status_filter
    )
