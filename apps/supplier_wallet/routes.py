# 📂 apps/supplier_wallet/routes.py

from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from datetime import datetime

supplier_wallet_bp = Blueprint('supplier_wallet', __name__, template_folder='templates')

@supplier_wallet_bp.route('/my-wallet', methods=['GET'])
@login_required
def view_my_wallet():
    # 1. جلب محفظة المورد (ضمان حماية المسار)
    wallet = SupplierWallet.query.filter_by(supplier_id=current_user.id).first()
    if not wallet:
        abort(404, description="لم يتم العثور على محفظة.")

    # 2. فلتر العملة (افتراضياً SAR)
    currency = request.args.get('currency', 'SAR')
    query = WalletTransaction.query.filter_by(wallet_id=wallet.id, currency=currency)

    # 3. البحث المرن (عبر AJAX أو التحديث العادي)
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (WalletTransaction.voucher_number.ilike(f'%{search}%')) | 
            (WalletTransaction.description.ilike(f'%{search}%'))
        )

    # 4. جلب كافة النتائج للحسابات الدقيقة (Pagination يتم لاحقاً)
    all_transactions = query.order_by(WalletTransaction.created_at.desc()).all()
    
    # 5. حساب الإجماليات (بناءً على العملة المختارة فقط)
    total_debit = sum(t.amount for t in all_transactions if t.trans_type == 'debit')
    total_credit = sum(t.amount for t in all_transactions if t.trans_type == 'credit')
    
    # 6. الترقيم
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 20
    offset = (page - 1) * per_page
    transactions_paginated = all_transactions[offset : offset + per_page]
    
    pagination = Pagination(page=page, total=len(all_transactions), per_page=per_page, css_framework='bootstrap5')

    # 7. استجابة الـ AJAX (تحديث الجدول والـ Footer فقط)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(
            'supplier_wallet/_table_partial.html', 
            transactions=transactions_paginated,
            total_debit=total_debit,
            total_credit=total_credit
        )

    # 8. الاستجابة العادية (تحميل الصفحة كاملة)
    return render_template(
        'supplier_wallet/supplier_wallet.html', 
        wallet=wallet,
        transactions=transactions_paginated, 
        pagination=pagination,
        total_debit=total_debit,
        total_credit=total_credit,
        now=datetime.utcnow()
    )
