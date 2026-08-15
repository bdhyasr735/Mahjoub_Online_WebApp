# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime

# استيراد قاعدة البيانات والنماذج الخاصة بك (قم بتعديل المسار حسب هيكل مشروعك الفعلي)
# from apps.extensions import db
# from apps.models.treasury import TreasuryLedger, BankAccount

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

    # استعلام قاعدة البيانات الحقيقي (بديل البيانات الوهمية)
    # query = TreasuryLedger.query

    # تطبيق فلتر البحث بالمرجع أو البيان
    # if search_query:
    #     query = query.filter(
    #         (TreasuryLedger.ref_code.ilike(f"%{search_query}%")) | 
    #         (TreasuryLedger.description.ilike(f"%{search_query}%"))
    #     )
    
    # if flow_type:
    #     query = query.filter(TreasuryLedger.flow_type == flow_type)

    # الجلب مع الترقيم (Pagination)
    # pagination = query.order_by(TreasuryLedger.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    # vouchers = pagination.items

    # مؤشرات الأداء الحقيقية (يمكن حسابها مباشرة من قاعدة البيانات)
    kpis = {
        "total_treasury_balance": 1845620.50, # استبدل بقيمة حقيقية مستخلصة من الحسابات
        "total_inflow": 2450890.00,
        "total_outflow": 605269.50,
        "escrow_reserve": 530200.00,
        "net_platform_profit": 194850.00,
        "currency": "SAR"
    }

    # جلب الحسابات البنكية الحقيقية من جدول البنوك
    # bank_accounts = BankAccount.query.all()
    bank_accounts = [] 

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        bank_accounts=bank_accounts,
        vouchers=[], # يتم تمرير المتغير الحقيقي هنا (vouchers)
        current_page=page,
        total_pages=1,
        filters={
            "q": search_query,
            "flow_type": flow_type
        }
    )

# ------------------ 2. مسار تفاصيل سند القيد الحقيقي ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    # جلب السند الحقيقي من قاعدة البيانات بناءً على الرمز المرجعي
    # voucher_data = TreasuryLedger.query.filter_by(ref_code=ref_code).first_or_404()
    
    voucher_data = None # سيتم تعبئتها من الاستعلام أعلاه

    if not voucher_data:
        abort(404)

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=voucher_data
    )
