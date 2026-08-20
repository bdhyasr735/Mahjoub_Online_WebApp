# -*- coding: utf-8 -*-
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet.services.wallet_service import WalletService
from apps.supplier_wallet.services.notification_service import NotificationService
from apps.supplier_wallet.utils import get_current_supplier_id

# استيراد البيانات مباشرة من ملفات الداتا
from apps.data.yemen_banks import YEMEN_BANKS
from apps.data.financial_companies import FINANCIAL_COMPANIES

supplier_wallet_bp = Blueprint(
    'supplier_wallet',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# ... (بقية دوال index و wallet_dashboard كما هي)

@supplier_wallet_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    supplier_id = get_current_supplier_id()
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    
    # دمج بيانات البنوك والشركات لعرضها في نموذج السحب
    available_banks = YEMEN_BANKS + FINANCIAL_COMPANIES

    if request.method == 'POST':
        try:
            amount = Decimal(request.form.get('amount', '0'))
            bank_name = request.form.get('bank_name', '') # نأخذ الاسم المختار من القائمة
            notes = request.form.get('notes', '').strip()

            wdr = WalletService.create_withdrawal_request(
                session=db.session,
                wallet_id=wallet.id,
                bank_account_id=bank_name, # سنخزن اسم البنك
                amount=amount,
                notes=notes
            )
            db.session.commit()
            flash('تم تقديم طلب السحب بنجاح.', 'success')
            return redirect(url_for('supplier_wallet.wallet_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'فشل تقديم طلب السحب: {str(e)}', 'error')

    return render_template(
        'supplier_wallet/withdrawal_form.html',
        wallet=wallet,
        bank_accounts=available_banks # نرسل القائمة المدمجة للقالب
    )
