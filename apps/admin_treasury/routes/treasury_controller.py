# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime, timedelta

# تحديد المسار: الصعود بمستوى واحد (من routes إلى admin_treasury) ثم الدخول لـ templates
basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

# 🔥 تعريف الـ Blueprint مع تحديد المسار المحلي للقوالب
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# ------------------ دوال الـ Routes ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    # بقية الكود كما هو...
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
        'admin/admin_treasury.html', # Flask سيبحث هنا: templates/admin/admin_treasury.html
        kpi=kpis,
        bank_accounts=bank_accounts,
        current_page=1,
        total_pages=5,
        filters={}
    )

@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    voucher_data = {
        "ref_code": ref_code,
        "voucher_number": "VCH-99201",
        "flow_type": "inflow",
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
        "description": "استلام قيمة الطلب رقم ORD-9928 بنجاح وإيداعها في حساب العمليات الرئيسي."
    }

    return render_template(
        'admin/admin_treasury_detail.html', # Flask سيبحث هنا: templates/admin/admin_treasury_detail.html
        voucher=voucher_data
    )
