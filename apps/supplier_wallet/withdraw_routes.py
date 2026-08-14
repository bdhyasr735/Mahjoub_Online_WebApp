# coding: utf-8
# 📂 apps/supplier_wallet/withdraw_routes.py

import secrets
import string
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import lazyload
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet, 
    get_registered_supplier_payout_info
)

# الحد الأدنى المسموح به لتقديم طلب سحب رصيد
MIN_WITHDRAW_AMOUNT = Decimal('50.00')


def generate_collision_proof_codes(supplier_id):
    """توليد رقم مرجعي ورقم سند محكمين للغاية ومقاومين للتصادم وتحت الضغط المتزامن."""
    now = datetime.utcnow()
    date_str = now.strftime('%Y%m%d')
    time_ms_str = now.strftime('%H%M%S%f')[:9]  # تتضمن الميكروثانية لضمان الدقة
    
    chars = string.ascii_uppercase + string.digits
    rand_ref = ''.join(secrets.choice(chars) for _ in range(4))
    rand_vch = ''.join(secrets.choice(chars) for _ in range(8))
    
    ref_number = f"TRX-SUPP{supplier_id}-{date_str}-{time_ms_str}-{rand_ref}"
    vch_number = f"VCH-{date_str}-{rand_vch}"
    
    return ref_number, vch_number


@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdraw():
    """عرض صفحة طلبات السحب ومعالجة تقديم طلب سحب جديد للمورد بطريقة محمية تماماً ضد الضغط الموازي."""
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
                flash("تعذر الوصول إلى حساب المحفظة الخاص بك.", "danger")
                return redirect(url_for('supplier_wallet.withdraw'))

            # =========================================================================
            # 🔒 [Pessimistic Locking بدون OUTER JOIN]: حجز المحفظة بأمان تام في PostgreSQL
            # =========================================================================
            locked_wallet = db.session.query(SupplierWallet)\
                .options(lazyload(SupplierWallet.supplier))\
                .filter(SupplierWallet.id == wallet_obj.id)\
                .with_for_update()\
                .first()

            if not locked_wallet:
                flash("تعذر تأمين حساب المحفظة، يرجى المحاولة لاحقاً.", "danger")
                return redirect(url_for('supplier_wallet.withdraw'))

            # التحقق من الرصيد الحقيقي المحدث بعد القفل (Prevent Race Condition)
            real_avail_bal = Decimal(str(getattr(locked_wallet, 'balance_sar', '0.00')))

            if real_avail_bal <= Decimal('0.00'):
                flash("رصيدك غير كافٍ، لا يوجد رصيد متاح للسحب حالياً.", "danger")
            elif amount > real_avail_bal:
                flash("رصيدك غير كافٍ لتغطية المبلغ المطلوب!", "danger")
            elif amount < MIN_WITHDRAW_AMOUNT:
                flash(f"الحد الأدنى لطلب السحب هو {float(MIN_WITHDRAW_AMOUNT):,.2f} {curr}", "danger")
            else:
                owner_name = registered_owner or f"مورد رقم #{supplier_id}"
                payout_label = "تحويل بنكي" if method == 'bank' else "شركات التحويل والصرافة"
                details_text = f" | التفاصيل: {registered_details}" if registered_details else ""
                
                # صياغة النص بحد أقصى 255 حرفاً
                full_desc = f"طلب سحب عبر {payout_label} | المالك: {owner_name}{details_text}"[:255]

                # توليد أرقام الترقيم والسند الفريدة محلياً بدقة الميكروثانية لضمان التحمل الكامل للضغط
                ref_num, vch_num = generate_collision_proof_codes(supplier_id)

                # إنشاء المعاملة بحقول جدول WalletTransaction الصحيحة
                new_tx = WalletTransaction(
                    wallet_id=locked_wallet.id,
                    owner_id=supplier_id,     
                    owner_type='supplier',   
                    trans_type='withdrawal',
                    status='pending',          # حالة الطلب الأولي: قيد المراجعة
                    amount=amount,
                    currency=curr,
                    reference_number=ref_num,
                    voucher_number=vch_num,
                    description=full_desc
                )

                db.session.add(new_tx)
                db.session.commit()

                flash(f"تم تقديم طلب السحب بنجاح برقم مرجعي: {ref_num} (سند: {vch_num})، وهو قيد المراجعة.", "success")
                return redirect(url_for('supplier_wallet.withdraw'))
                
        except (ValueError, InvalidOperation):
            db.session.rollback()
            flash("يرجى إدخال مبلغ مالي صحيح.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ غير متوقع أثناء حفظ الطلب: {str(e)}", "danger")

    # استعلام واستعراض سجل عمليات السحب (GET)
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)
    query = query.filter(WalletTransaction.trans_type == 'withdrawal')

    if status_filter != 'all':
        query = query.filter(WalletTransaction.status == status_filter)

    pagination_obj = query.order_by(
        WalletTransaction.created_at.desc(), 
        WalletTransaction.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

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