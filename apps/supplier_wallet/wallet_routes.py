# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.extensions import db, limiter
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.supplier_wallet import supplier_wallet_bp
from apps.supplier_wallet.utils import (
    get_current_supplier_id, 
    get_or_create_supplier_wallet
)

@supplier_wallet_bp.route('/', methods=['GET'], strict_slashes=False, endpoint='wallet_dashboard')
@supplier_wallet_bp.route('/dashboard', methods=['GET'], strict_slashes=False, endpoint='wallet_home')
@login_required
@limiter.exempt
def wallet_dashboard():
    """لوحة تحكم المحفظة الرئيسية للمورد (عرض الأرصدة، الملخص المالي، وآخر المعاملات المعتمدة)."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    # تجهيز ملخص المحفظة
    summary = {
        'available_balance': float(wallet_obj.balance_sar) if wallet_obj and wallet_obj.balance_sar else 0.00,
        'pending_balance': float(wallet_obj.balance_pending) if wallet_obj and wallet_obj.balance_pending else 0.00,
        'total_withdrawn': float(wallet_obj.total_withdrawn) if wallet_obj and wallet_obj.total_withdrawn else 0.00,
        'currency': getattr(wallet_obj, 'default_currency', 'SAR'),
        'wallet_code': getattr(wallet_obj, 'wallet_code', f"WEL-{supplier_id}")
    }

    # معاملات البحث والفلترة والصفحات
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    # المنطق البرمجي: إذا لم يحدد المستخدم فلتر حالة معين، نستبعد المعاملات المعلقة (pending) من الكشف المالي الأساسي
    if status_filter == 'all':
        query = query.filter(WalletTransaction.status != 'pending')
    else:
        query = query.filter(WalletTransaction.status == status_filter)
    
    if type_filter != 'all':
        query = query.filter(WalletTransaction.trans_type == type_filter)

    pagination_obj = query.order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        wallet=wallet_obj,
        transactions=pagination_obj.items,
        pagination=pagination_obj,
        active_status=status_filter,
        active_type=type_filter
    )


@supplier_wallet_bp.route('/print-statement', methods=['GET'], endpoint='wallet_print_statement')
@login_required
def wallet_print_statement():
    """عرض كشف حساب المورد بصيغة مهيأة للطباعة (PDF)."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    
    if not wallet_obj:
        return "المحفظة غير موجودة", 404

    # تجهيز الملخص (إجمالي شامل لغايات الكشف)
    summary = {
        'total_balance': float(wallet_obj.balance_sar or 0.00) + float(wallet_obj.balance_pending or 0.00),
        'available_balance': float(wallet_obj.balance_sar or 0.00),
        'total_withdrawn': float(wallet_obj.total_withdrawn or 0.00),
        'currency': getattr(wallet_obj, 'default_currency', 'SAR')
    }

    # جلب كافة المعاملات المكتملة لعرضها في الكشف (بدون صفحات)
    transactions = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id)\
        .filter(WalletTransaction.status != 'pending')\
        .order_by(WalletTransaction.created_at.desc())\
        .all()

    return render_template(
        'supplier_wallet/wallet_pdf_print.html',
        summary=summary,
        transactions=transactions,
        current_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )


@supplier_wallet_bp.route('/api/summary', methods=['GET'], strict_slashes=False, endpoint='wallet_api_summary')
@login_required
def wallet_api_summary():
    """API جلب الملخص المالي للمحفظة (تحديث حي عبر الـ AJAX)."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)

    if not wallet_obj:
        return jsonify({"status": "error", "message": "المحفظة غير موجودة."}), 404

    return jsonify({
        "status": "success",
        "data": {
            "available_balance": float(wallet_obj.balance_sar or 0.00),
            "pending_balance": float(wallet_obj.balance_pending or 0.00),
            "total_withdrawn": float(wallet_obj.total_withdrawn or 0.00),
            "currency": getattr(wallet_obj, 'default_currency', 'SAR'),
            "wallet_code": getattr(wallet_obj, 'wallet_code', '')
        }
    }), 200
