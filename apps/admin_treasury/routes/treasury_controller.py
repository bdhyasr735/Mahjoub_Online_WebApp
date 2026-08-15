# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime, timedelta

# تحديد المسار: الصعود بمستوى واحد (من routes إلى admin_treasury) ثم الدخول لـ templates
basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

# تعريف الـ Blueprint مع تحديد المسار المحلي للقوالب
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# بيانات وهمية افتراضية شاملة لقيود الخزينة (سيتم استبدالها لاحقاً بقاعدة البيانات مباشرة)
DUMMY_VOUCHERS_LIST = [
    {
        "ref_code": "TRZ-2026-0841",
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
        "description": "استلام قيمة الطلب وإيداعها في حساب العمليات الرئيسي بنجاح."
    },
    {
        "ref_code": "TRZ-2026-0840",
        "voucher_number": "VCH-99200",
        "flow_type": "outflow",
        "category_label": "مستحقات شركاء وموردين",
        "amount": 45000.00,
        "balance_after": 1833170.50,
        "currency": "SAR",
        "status": "completed",
        "source_destination": "مستحقات شركة الرياض للتوريدات",
        "payment_method": "تحويل بنكي مباشر",
        "admin_reviewer": "أ. علي المحجوب",
        "created_at": "2026-08-14 10:15",
        "settled_at": "2026-08-14 10:20",
        "description": "سداد دفعة مستحقة نظير توريد بضائع للمستودع المركزي."
    },
    {
        "ref_code": "TRZ-2026-0839",
        "voucher_number": "VCH-99199",
        "flow_type": "inflow",
        "category_label": "حجز ضمانات شحنات",
        "amount": 8200.00,
        "balance_after": 1878170.50,
        "currency": "SAR",
        "status": "completed",
        "source_destination": "حجز ضمان طلبيات #SHP-401",
        "payment_method": "محفظة النظام الداخلية",
        "admin_reviewer": "النظام الآلي",
        "created_at": "2026-08-13 18:40",
        "settled_at": "2026-08-13 18:40",
        "description": "تجميد مبلغ ضمان مؤقت لحين استلام الشحنة من قبل العميل."
    }
]

# ------------------ 1. مسار القائمة الرئيسية (الخزينة والقيود مع تفعيل البحث) ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    # استلام فلاتر البحث والترقيم
    search_query = request.args.get('q', '').strip()
    flow_type = request.args.get('flow_type', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)

    # تطبيق تصفية البحث بالمرجع أو البيان إذا وجد
    filtered_vouchers = DUMMY_VOUCHERS_LIST
    if search_query:
        filtered_vouchers = [
            v for v in filtered_vouchers 
            if search_query.lower() in v['ref_code'].lower() 
            or search_query.lower() in v['source_destination'].lower()
            or search_query.lower() in v['description'].lower()
        ]

    if flow_type:
        filtered_vouchers = [v for v in filtered_vouchers if v['flow_type'] == flow_type]

    # بيانات مؤشرات الأداء العامة (KPIs)
    kpis = {
        "total_treasury_balance": 1845620.50,
        "total_inflow": 2450890.00,
        "total_outflow": 605269.50,
        "escrow_reserve": 530200.00,
        "net_platform_profit": 194850.00,
        "currency": "SAR"
    }

    # الحسابات البنكية ومحافظ التسوية
    bank_accounts = [
        {"id": 1, "bank_name": "مصرف الراجحي", "account_number": "SA8820000001234567890123", "account_type": "حساب العمليات الرئيسي", "current_balance": 1120450.00, "currency": "SAR"},
        {"id": 2, "bank_name": "البنك الأهلي السعودي (SNB)", "account_number": "SA4410000009876543210987", "account_type": "حساب ضمان المشتريات (Escrow)", "current_balance": 530200.00, "currency": "SAR"},
        {"id": 3, "bank_name": "بنك الرياض", "account_number": "SA1230000005544332211002", "account_type": "حساب الاحتياطي والتسويات", "current_balance": 194970.50, "currency": "SAR"}
    ]

    return render_template(
        'admin/admin_treasury.html',
        kpi=kpis,
        bank_accounts=bank_accounts,
        vouchers=filtered_vouchers,
        current_page=page,
        total_pages=1,
        filters={
            "q": search_query,
            "flow_type": flow_type,
            "category": category
        }
    )

# ------------------ 2. مسار تفاصيل سند القيد ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    # البحث عن السند في القائمة المتاحة أو إنشاء هيكل افتراضي متناسق إن لم يوجد
    voucher_data = next((v for v in DUMMY_VOUCHERS_LIST if v['ref_code'] == ref_code), None)
    
    if not voucher_data:
        # سند افتراضي في حال تم كتابة مرجع غير موجود
        voucher_data = {
            "ref_code": ref_code,
            "voucher_number": "VCH-00000",
            "flow_type": "inflow",
            "category_label": "قيد تسوية عام",
            "amount": 0.00,
            "balance_after": 1845620.50,
            "currency": "SAR",
            "status": "verified",
            "source_destination": "غير محدد",
            "payment_method": "نظام قيود الخزينة المركزي",
            "admin_reviewer": "النظام الآلي",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "settled_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": "قيد مالي معتمد داخل المنظومة السيادية."
        }

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=voucher_data
    )
