# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime

# استيراد قاعدة البيانات والنماذج الفعلية للنظام
from apps.extensions import db
from apps.models.treasury import TreasuryLedger, BankAccount

basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# ------------------ 1. مسار القائمة الرئيسية (تصفية حقيقية بالمرجع بدون بيانات وهمية) ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    search_query = request.args.get('q', '').strip()
    flow_type = request.args.get('flow_type', '').strip()
    page = request.args.get('page', 1, type=int)

    # الاستعلام الأساسي من قاعدة البيانات
    query = TreasuryLedger.query

    # تطبيق البحث الحي والمباشر برمز المرجع أو البيان
    if search_query:
        query = query.filter(
            (TreasuryLedger.ref_code.ilike(f"%{search_query}%")) | 
            (TreasuryLedger.description.ilike(f"%{search_query}%")) |
            (TreasuryLedger.source_destination.ilike(f"%{search_query}%"))
        )
    
    # تصفية نوع التدفق (وارد / صادر) إن وجد
    if flow_type:
        query = query.filter(TreasuryLedger.flow_type == flow_type)

    # جلب البيانات مع الترقيم التلقائي
    pagination = query.order_by(TreasuryLedger.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    vouchers = pagination.items

    # حساب المؤشرات المالية الحقيقية بناءً على قاعدة البيانات (أو تركها كقيم إجمالية حية)
    total_inflow = db.session.query(db.func.sum(TreasuryLedger.amount)).filter(TreasuryLedger.flow_type == 'inflow').scalar() or 0.0
    total_outflow = db.session.query(db.func.sum(TreasuryLedger.amount)).filter(TreasuryLedger.flow_type == 'outflow').scalar() or 0.0
    
    kpis = {
        "total_treasury_balance": total_inflow - total_outflow,
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "escrow_reserve": 530200.00, # يمكن ربطها بجدول الأمانات الخاص إن وجد
        "currency": "SAR"
    }

    # جلب الحسابات البنكية الفعلية
    bank_accounts = BankAccount.query.all()

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        bank_accounts=bank_accounts,
        vouchers=vouchers,
        pagination=pagination,
        filters={
            "q": search_query,
            "flow_type": flow_type
        }
    )

# ------------------ 2. مسار تفاصيل السند الحقيقي ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    # جلب السند الحقيقي مباشرة من قاعدة البيانات
    voucher_data = TreasuryLedger.query.filter_by(ref_code=ref_code).first_or_404()

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=voucher_data
    )
