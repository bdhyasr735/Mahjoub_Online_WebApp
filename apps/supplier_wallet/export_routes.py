# coding: utf-8
# 📂 apps/supplier_wallet/export_routes.py

from datetime import datetime
from flask import render_template, request
from flask_login import login_required
from apps.extensions import db
from apps.models.wallet_db import WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet
)

@supplier_wallet_bp.route('/wallet/export-pdf', methods=['GET'], strict_slashes=False, endpoint='export_wallet_pdf')
@supplier_wallet_bp.route('/withdraw/export-pdf', methods=['GET'], strict_slashes=False, endpoint='export_wallet_pdf')
@login_required
def export_wallet_pdf():
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # تجهيز الملخص مباشرة من خصائص الموديل المحفوظة
    summary = {
        'total_balance': float(wallet_obj.balance_sar or 0.0) if wallet_obj else 0.0,
        'available_balance': float(wallet_obj.balance_sar or 0.0) if wallet_obj else 0.0,
        'pending_balance': float(wallet_obj.balance_pending or 0.0) if wallet_obj else 0.0,
        'total_withdrawn': float(wallet_obj.total_withdrawn or 0.0) if wallet_obj else 0.0,
        'currency': 'SAR'
    }

    # تحديد الاستعلام بناءً على الرابط (محفظة عامة أم طلبات سحب)
    is_withdraw_path = 'withdraw' in request.path
    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    # تعريف مصفوفات أنواع الحركات للفلترة الذكية المتوافقة مع الواجهة
    credit_types = ['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit']
    debit_types = ['debit', 'withdrawal', 'commission_deduction', 'adjustment_debit']

    if is_withdraw_path:
        query = query.filter(WalletTransaction.trans_type == 'withdrawal')
        # فلترة الحالة لطلبات السحب إذا تم تمريرها
        status = request.args.get('status', '')
        if status:
            query = query.filter(WalletTransaction.status == status)
    else:
        # 🛑 القاعدة الصارمة: كشف حساب المحفظة العامة يعرض الحركات المكتملة فقط حصرياً
        query = query.filter(WalletTransaction.status == 'completed')

        # فلاتر المحفظة العامة للنوع
        trx_type = request.args.get('type', '')
        if trx_type == 'credit':
            query = query.filter(WalletTransaction.trans_type.in_(credit_types))
        elif trx_type == 'debit':
            query = query.filter(WalletTransaction.trans_type.in_(debit_types))

    # تصفية بالتاريخ إن وجد في الـ Query Parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WalletTransaction.created_at >= parsed_start)
        except ValueError:
            pass

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(WalletTransaction.created_at <= parsed_end)
        except ValueError:
            pass

    transactions = query.order_by(WalletTransaction.created_at.desc(), WalletTransaction.id.desc()).all()

    return render_template(
        'supplier_wallet/wallet_pdf_print.html',
        summary=summary,
        transactions=transactions,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
