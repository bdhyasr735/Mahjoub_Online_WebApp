# coding: utf-8
# 📂 apps/wallet/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from apps.extensions import db
from sqlalchemy import or_

wallet_bp = Blueprint('wallet_app', __name__, template_folder='templates')

# ... (دالة dashboard تبقى كما هي بدون تغيير) ...

@wallet_bp.route('/admin/manage/<int:supplier_id>/add_transaction', methods=['POST'])
@login_required
def add_transaction(supplier_id):
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    amount = float(request.form.get('amount', 0))
    trans_type = request.form.get('type')  # 'credit' أو 'debit'
    currency = request.form.get('currency')
    ref = request.form.get('reference_number')
    desc = request.form.get('description')

    if amount <= 0:
        flash("يجب أن يكون المبلغ أكبر من صفر.", "danger")
        return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))

    try:
        # [تحسين محاسبي]: التأكد من توفر رصيد قبل السحب
        if trans_type == 'debit':
            if currency == 'SAR' and wallet.balance_sar < amount:
                flash("رصيد SAR غير كافٍ للعملية.", "danger")
                return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
            # (يمكنك إضافة التحقق لبقية العملات هنا بنفس المنطق)

        # تحديث الرصيد
        if currency == 'SAR':
            wallet.balance_sar += amount if trans_type == 'credit' else -amount
        elif currency == 'YER':
            wallet.balance_yer += amount if trans_type == 'credit' else -amount
        elif currency == 'USD':
            wallet.balance_usd += amount if trans_type == 'credit' else -amount

        # إنشاء القيد
        new_trans = WalletTransaction(
            wallet_id=wallet.id,
            trans_type=trans_type,
            source_type='voucher',
            amount=amount,
            currency=currency,
            reference_number=ref,
            description=desc
        )
        
        db.session.add(new_trans)
        db.session.commit()
        flash(f"تم تسجيل السند {ref} بنجاح.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash("حدث خطأ تقني أثناء معالجة السند.", "danger")

    return redirect(url_for('wallet_app.manage_wallet', supplier_id=supplier_id))
