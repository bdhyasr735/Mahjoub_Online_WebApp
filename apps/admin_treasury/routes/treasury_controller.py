# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from decimal import Decimal

from apps.extensions import db
from apps.models.wallet_db import WalletTransaction, SupplierWallet

basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# ------------------ 1. مسار القائمة الرئيسية (سجل الحركات المالية الكاملة) ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    search_query = request.args.get('q', '').strip()
    trans_type_filter = request.args.get('trans_type', '').strip()
    page = request.args.get('page', 1, type=int)

    # الاستعلام المباشر من جدول الحركات المالية الكاملة
    query = WalletTransaction.query

    # تطبيق البحث الشامل برقم السند أو المرجع
    if search_query:
        query = query.filter(
            (WalletTransaction.reference_number.ilike(f"%{search_query}%")) | 
            (WalletTransaction.voucher_number.ilike(f"%{search_query}%"))
        )
    
    # تصفية نوع الحركة (دخول، خروج، توزيع...)
    if trans_type_filter:
        query = query.filter(WalletTransaction.trans_type == trans_type_filter)

    # الترقيم (Pagination) بمعدل 15 حركة لكل صفحة
    pagination = query.order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    transactions = pagination.items

    # حساب الإجماليات بدقة تامة باستخدام Decimal لحساب كل هللة
    raw_inflow = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.trans_type.in_(['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit'])
    ).scalar()
    total_inflow = Decimal(str(raw_inflow)) if raw_inflow is not None else Decimal('0.00')

    raw_outflow = db.session.query(db.func.sum(WalletTransaction.amount)).filter(
        ~WalletTransaction.trans_type.in_(['credit', 'sale_revenue', 'deposit', 'refund', 'adjustment_credit'])
    ).scalar()
    total_outflow = Decimal(str(raw_outflow)) if raw_outflow is not None else Decimal('0.00')

    net_balance = total_inflow - total_outflow

    kpis = {
        "total_treasury_balance": net_balance,
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "currency": "SAR"
    }

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        transactions=transactions,
        pagination=pagination,
        filters={
            "q": search_query,
            "trans_type": trans_type_filter
        }
    )

# ------------------ 2. مسار تفاصيل الحركة المالية الكاملة ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    # البحث برقم المرجع أو رقم السند لعرض تفاصيل الحركة الكاملة
    transaction = WalletTransaction.query.filter(
        (WalletTransaction.reference_number == ref_code) | 
        (WalletTransaction.voucher_number == ref_code)
    ).first_or_404()

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=transaction
    )
