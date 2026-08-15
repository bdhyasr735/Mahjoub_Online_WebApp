# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/treasury_controller.py

import os
from flask import Blueprint, render_template, request, abort
from datetime import datetime
from sqlalchemy import func, or_

from apps.extensions import db
from apps.models.treasury_db import TreasuryEntry
from apps.models.financials_db import OrderFinancial
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet

basedir = os.path.abspath(os.path.dirname(__file__))
template_folder_path = os.path.abspath(os.path.join(basedir, '../templates'))

admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder=template_folder_path,
    url_prefix='/admin/treasury'
)

# قاموس موحد لترجمة أنواع الحركات المالية إلى العربية
ENTRY_TYPE_TRANSLATIONS = {
    'deposit': 'إيداع نقدي',
    'revenue_net': 'صافي إيرادات مبيعات',
    'supplier_settlement': 'تسوية مستحقات مورد',
    'affiliate_payout': 'عمولة مسوق بالعمولة',
    'operational_cost': 'تكلفة تشغيلية'
}

def enrich_voucher_data(voucher):
    """تحويل السجل إلى كائن مرن آمن يحمل كافة الخصائص الحقيقية للمتجر والمحفظة"""
    if not voucher:
        return None
    
    raw_type = str(getattr(voucher, 'entry_type', '') or '').strip()
    localized_type = ENTRY_TYPE_TRANSLATIONS.get(raw_type, raw_type)
    
    created_at = getattr(voucher, 'created_at', None)
    try:
        if created_at and hasattr(created_at, 'strftime'):
            formatted_time = created_at.strftime('%Y-%m-%d %H:%M')
        else:
            formatted_time = str(created_at) if created_at else '-'
    except Exception:
        formatted_time = '-'

    owner_type = getattr(voucher, 'owner_type', 'عام') or 'عام'
    owner_id = getattr(voucher, 'owner_id', None)

    # جلب بيانات المورد والمحفظة الحقيقية من قاعدة البيانات لربط الأكواد والأسماء بدقة
    store_name_val = None
    owner_name_val = None
    wallet_code_val = None
    supplier_code_val = None

    if owner_id and str(owner_id).isdigit():
        supplier_obj = db.session.get(Supplier, int(owner_id))
        if supplier_obj:
            store_name_val = supplier_obj.store_name or supplier_obj.trade_name or supplier_obj.username
            owner_name_val = supplier_obj.owner_name
            supplier_code_val = supplier_obj.supplier_code or f"SUP-963{supplier_obj.id}"
            
            if supplier_obj.wallet:
                wallet_code_val = supplier_obj.wallet.wallet_code

        # Fallback للبحث عن المحفظة مباشرة إذا لم تكن مرتبطة عبر العلاقة العكسية
        if not wallet_code_val:
            wallet_obj = SupplierWallet.query.filter_by(supplier_id=int(owner_id)).first()
            if wallet_obj:
                wallet_code_val = wallet_obj.wallet_code

    # استخدام القيم الافتراضية المنسجمة مع نظامك النمطي إذا لم توجد بيانات
    final_store_name = store_name_val or f"متجر الطرف ({owner_type})"
    final_owner_name = owner_name_val or f"مستخدم نظام ID: {owner_id or 'N/A'}"
    final_wallet_code = wallet_code_val or (f"WEL-963{owner_id}" if owner_id else "WEL-963X")
    final_supplier_code = supplier_code_val or (f"SUP-963{owner_id}" if owner_id else "SUP-963X")

    class VoucherWrapper:
        def __init__(self, original_obj, loc_type, fmt_time):
            self._original = original_obj
            self.localized_entry_type = loc_type
            self.formatted_time = fmt_time
            self.created_at = created_at
            self.reference_number = getattr(original_obj, 'reference_number', '-')
            self.voucher_number = getattr(original_obj, 'voucher_number', '-')
            self.order_id = getattr(original_obj, 'order_id', None)
            self.amount = getattr(original_obj, 'amount', 0.0)
            self.entry_type = raw_type
            self.owner_type = owner_type
            self.owner_id = owner_id
            self.owner_details = {
                "store_name": final_store_name,
                "owner_name": final_owner_name,
                "wallet_code": final_wallet_code,
                "supplier_code": final_supplier_code
            }

        def __getattr__(self, name):
            try:
                return getattr(self._original, name)
            except Exception:
                return None

    return VoucherWrapper(voucher, localized_type, formatted_time)

# ------------------ 1. مسار القائمة الرئيسية (الخزينة والقيود الحقيقية) ------------------
@admin_treasury_bp.route('/', methods=['GET'])
def treasury_index():
    search_query = request.args.get('q', '').strip()
    flow_type = request.args.get('flow_type', '').strip()
    page = request.args.get('page', 1, type=int)

    try:
        query = TreasuryEntry.query

        if search_query:
            query = query.filter(
                or_(
                    TreasuryEntry.reference_number.ilike(f"%{search_query}%"),
                    TreasuryEntry.voucher_number.ilike(f"%{search_query}%"),
                    TreasuryEntry.owner_type.ilike(f"%{search_query}%")
                )
            )
        
        if flow_type:
            query = query.filter(TreasuryEntry.entry_type == flow_type)

        # التعديل هنا: جعل عدد الحركات في كل صفحة 10 حركات בדיוק
        pagination = query.order_by(TreasuryEntry.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        
        # إثراء السجلات بالترجمة والخصائص الآمنة
        vouchers = [enrich_voucher_data(v) for v in pagination.items]

        try:
            total_suppliers_cost = db.session.query(func.sum(OrderFinancial.supplier_cost_raw)).scalar() or 0.0
            total_platform_profit = db.session.query(func.sum(OrderFinancial.mahjoub_commission_raw)).scalar() or 0.0
        except Exception:
            total_suppliers_cost = 0.0
            total_platform_profit = 0.0
        
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
    except Exception as e:
        print(f"❌ [Treasury Error]: {str(e)}")
        return render_template(
            'admin/admin_treasury.html',
            kpi={"total_treasury_balance": 0.0, "total_inflow": 0.0, "total_outflow": 0.0, "escrow_reserve": 0.0, "net_platform_profit": 0.0, "currency": "SAR"},
            bank_accounts=[],
            vouchers=[],
            current_page=1,
            total_pages=1,
            filters={"q": "", "flow_type": ""}
        )

# ------------------ 2. مسار تفاصيل سند القيد الحقيقي ------------------
@admin_treasury_bp.route('/detail/<string:ref_code>', methods=['GET'])
def treasury_detail(ref_code):
    voucher_data = TreasuryEntry.query.filter(
        or_(
            TreasuryEntry.reference_number == ref_code,
            TreasuryEntry.voucher_number == ref_code
        )
    ).first()
    
    if not voucher_data:
        abort(404)

    # إثراء السند المنفرد بالبيانات المترجمة
    enriched_voucher = enrich_voucher_data(voucher_data)

    return render_template(
        'admin/admin_treasury_detail.html',
        voucher=enriched_voucher
    )
