# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime
from sqlalchemy import func

from apps.extensions import db
from apps.models.treasury_db import TreasuryEntry
from apps.models.financials_db import OrderFinancial
from apps.models.supplier_db import Supplier

basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# ------------------ 1. مسار القائمة الرئيسية (الخزينة والقيود الحقيقية) ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    search_query = request.args.get('q', '').strip()
    flow_type = request.args.get('flow_type', '').strip()
    page = request.args.get('page', 1, type=int)

    # الاستعلام الأساسي بدون علاقات معقدة تسبب انهيار النظام
    query = TreasuryEntry.query

    # تطبيق فلتر البحث بالمرجع أو البيان أو نوع الطرف
    if search_query:
        query = query.filter(
            (TreasuryEntry.reference_number.ilike(f"%{search_query}%")) | 
            (TreasuryEntry.owner_type.ilike(f"%{search_query}%"))
        )
    
    if flow_type:
        query = query.filter(TreasuryEntry.entry_type == flow_type)

    # الجلب مع الترقيم (Pagination)
    pagination = query.order_by(TreasuryEntry.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    vouchers = pagination.items

    # حساب مؤشرات الأداء الحقيقية والمطابقة محاسبياً (SAR)
    total_suppliers_cost = db.session.query(func.sum(OrderFinancial.supplier_cost_raw)).scalar() or 0.0
    total_platform_profit = db.session.query(func.sum(OrderFinancial.mahjoub_commission_raw)).scalar() or 0.0
    
    # إجمالي حركات الخزينة المسجلة
    total_inflow = db.session.query(func.sum(TreasuryEntry.amount)).filter(TreasuryEntry.entry_type.in_(['revenue_net', 'deposit'])).scalar() or 0.0
    total_outflow = db.session.query(func.sum(TreasuryEntry.amount)).filter(TreasuryEntry.entry_type.in_(['supplier_settlement', 'affiliate_payout', 'operational_cost'])).scalar() or 0.0
    
    total_treasury_balance = float(total_inflow) - float(total_outflow)

    kpis = {
        "total_treasury_balance": float(total_treasury_balance),
        "total_inflow": float(total_inflow),
        "total_outflow": float(total_outflow),
        "escrow_reserve": float(total_suppliers_cost), 
        "net_platform_profit": float(total_platform_profit), 
        "currency": "SAR"
    }

    bank_accounts = [] 

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        bank_accounts=bank_accounts,
        vouchers=vouchers,
        current_page=page,
        total_pages=pagination.pages if pagination.pages > 0 else 1,
        filters={
            "q": search_query,
            "flow_type": flow_type
        }
    )

# ------------------ 2. مسار تفاصيل سند القيد الحقيقي ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    # جلب السند بشكل مباشر وآمن بدون استخدام joinedload المسببة للأخطاء
    voucher_data = TreasuryEntry.query.filter_by(reference_number=ref_code).first()
    
    if not voucher_data:
        abort(404)

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=voucher_data
    )
