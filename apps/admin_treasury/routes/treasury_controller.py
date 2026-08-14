# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py
"""
متحكم وإدارة مسارات الرقابة المالية (الخزينة المركزية) وحسابات الضمان
مشروع Mahjoub Online WebApp
"""

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime, timedelta

# تحديد المسار المطلق لمجلد القوالب الرئيسي للمشروع بدقة لتجنب أخطاء المسارات النسبية
basedir = os.path.abspath(os.path.dirname(__file__))
# مسار الوصول لمجلد templates العام للمشروع من داخل مجلد الـ routes الحالي
templates_path = os.path.abspath(os.path.join(basedir, '../../templates'))

# 🔥 تعريف الـ Blueprint مع تمرير المسار المطلق الصحيح للقوالب
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=templates_path,
    url_prefix='/admin/treasury'
)

# ------------------ دوال الـ Routes ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    """
    عرض لوحة الرقابة المالية والخزينة المركزية: المؤشرات، الأرصدة، والقيود
    """
    page = request.args.get('page', 1, type=int)
    flow_type = request.args.get('flow_type', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    search_q = request.args.get('q', '').strip()
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    kpis = {
        "total_treasury_balance": 1845620.50,
        "total_inflow": 2450890.00,
        "total_outflow": 605269.50,
        "escrow_reserve": 530200.00,
        "net_platform_profit": 194850.00,
        "currency": "SAR"
    }

    bank_accounts = [
        {"id": 1, "bank_name": "مصرف الراجحي", "account_number": "SA8820000001234567890123", "account_type": "حساب العمليات الرئيسي", "current_balance": 1120450.00, "currency": "SAR"},
        {"id": 2, "bank_name": "البنك الأهلي السعودي (SNB)", "account_number": "SA4410000009876543210987", "account_type": "حساب ضمان المشتريات (Escrow)", "current_balance": 530200.00, "currency": "SAR"},
        {"id": 3, "bank_name": "بنك الرياض", "account_number": "SA1230000005544332211002", "account_type": "حساب الاحتياطي والتسويات", "current_balance": 194970.50, "currency": "SAR"}
    ]

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        bank_accounts=bank_accounts,
        current_page=page,
        total_pages=5,
        filters={
            "flow_type": flow_type,
            "category": category,
            "status": status,
            "q": search_q,
            "start_date": start_date,
            "end_date": end_date
        }
    )

@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    """
    استعراض تفاصيل وسند قيد محدد من الخزينة المركزية
    """
    if not ref_code or len(ref_code.strip()) == 0:
        abort(404)

    voucher_data = {
        "ref_code": ref_code,
        "voucher_number": "VCH-99201",
        "flow_type": "inflow",
        "category": "order_payment",
        "category_label": "سداد مبيعات إلكترونية",
        "amount": 12450.00,
        "balance_after": 1845620.50,
        "currency": "SAR",
        "status": "completed",
        "source_destination": "سداد طلبية مشتريات #ORD-9928",
        "payment_method": "مدى / بطاقة ائتمان (الراجحي)",
        "admin_reviewer": "أ. محمد السليمان (مدير الحسابات)",
        "created_at": "2026-08-14 14:30",
        "settled_at": "2026-08-14 14:31",
        "description": "استلام قيمة الطلب رقم ORD-9928 بنجاح وإيداعها في حساب العمليات الرئيسي مع استقطاع عمولة المنصة."
    }

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=voucher_data
    )
