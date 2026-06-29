# coding: utf-8
# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from apps.supplier_wallet.services import WalletService

supplier_wallet_bp = Blueprint(
    'supplier_wallet', 
    __name__, 
    template_folder='templates'
)

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # 1. جلب المحفظة
    wallet = getattr(current_user, 'wallet', None)
    if not wallet:
        wallet = WalletService.get_supplier_wallet(current_user.id)
    
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة مرتبطة بحسابك.")

    # 2. حساب الإجماليات (محرك المحاسبة في الخلفية)
    # نقوم بفرز العمليات حسابياً قبل إرسالها للقالب لتسهيل عرض الخلاصة
    total_debit = sum(t.amount for t in wallet.transactions if t.trans_type == 'debit')
    total_credit = sum(t.amount for t in wallet.transactions if t.trans_type == 'credit')

    # 3. تمرير الإجماليات مع المحفظة للقالب
    return render_template(
        'supplier_wallet/supplier_wallet.html', 
        wallet=wallet,
        total_debit=total_debit,
        total_credit=total_credit
    )
