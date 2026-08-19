# coding: utf-8
# 📂 apps/supplier_wallet/wallet_routes.py

from datetime import datetime
from flask import render_template, request, jsonify, abort
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
    search_query = request.args.get('q', '').strip() or request.args.get('search', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id if wallet_obj else -1)

    # فلتر الحالة
    if status_filter == 'all':
        query = query.filter(WalletTransaction.status != 'pending')
    else:
        query = query.filter(WalletTransaction.status == status_filter)
    
    # فلتر النوع
    if type_filter and type_filter != 'all':
        query = query.filter(WalletTransaction.trans_type == type_filter)

    # البحث اللحظي (في رقم المرجع أو البيان أو رقم الحوالة)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                WalletTransaction.reference_number.ilike(search_term),
                WalletTransaction.description.ilike(search_term),
                WalletTransaction.transfer_number.ilike(search_term)
            )
        )

    # فلتر نطاق التاريخ (من وإلى)
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WalletTransaction.created_at >= parsed_start)
        except ValueError:
            pass

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(WalletTransaction.created_at <= parsed_end)
        except ValueError:
            pass

    pagination_obj = query.order_by(WalletTransaction.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    # 🛡️ طبقة تجهيز البيانات وضمان الاستمرارية (Data Preparation Layer)
    processed_transactions = []
    for tx in pagination_obj.items:
        # تجهيز الخصائص بأمان لضمان عدم ظهور أي أخطاء في القالب
        tx.display_bank = getattr(tx, 'bank_name', None) or 'غير محدد'
        tx.display_beneficiary = getattr(tx, 'beneficiary_name', None) or 'غير محدد'
        tx.display_transfer_no = getattr(tx, 'transfer_number', None) or tx.reference_number or '-'
        processed_transactions.append(tx)

    return render_template(
        'supplier_wallet/wallet.html',
        summary=summary,
        wallet=wallet_obj,
        transactions=processed_transactions,
        pagination=pagination_obj,
        active_status=status_filter,
        active_type=type_filter
    )


@supplier_wallet_bp.route('/voucher/<voucher_code>', methods=['GET'], endpoint='view_voucher_detail')
@login_required
def view_voucher_detail(voucher_code):
    """عرض صفحة تفاصيل السند المستقلة الخاصة بالمورد."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    
    if not wallet_obj:
        abort(404)

    # البحث عن الحركة إما برقم المرجع أو كود السند أو المعرف، بشرط أن تخص محفظة المورد الحالي
    transaction = WalletTransaction.query.filter(
        WalletTransaction.wallet_id == wallet_obj.id,
        db.or_(
            WalletTransaction.reference_number == voucher_code,
            WalletTransaction.voucher_code == voucher_code
        )
    ).first_or_404()

    # تجهيز خصائص العرض للسند
    transaction.display_bank = getattr(transaction, 'bank_name', None) or 'غير محدد'
    transaction.display_beneficiary = getattr(transaction, 'beneficiary_name', None) or 'غير محدد'
    transaction.display_transfer_no = getattr(transaction, 'transfer_number', None) or transaction.reference_number or '-'

    return render_template(
        'supplier_wallet/voucher_detail.html',
        transaction=transaction,
        wallet=wallet_obj
    )


@supplier_wallet_bp.route('/print-statement', methods=['GET'], endpoint='wallet_print_statement')
@login_required
def wallet_print_statement():
    """عرض كشف حساب المورد بصيغة مهيأة للطباعة (PDF) مع دعم الفلترة الحالية."""
    supplier_id = get_current_supplier_id()
    wallet_obj = get_or_create_supplier_wallet(supplier_id)
    
    if not wallet_obj:
        return "المحفظة غير موجودة", 404

    summary = {
        'total_balance': float(wallet_obj.balance_sar or 0.00) + float(wallet_obj.balance_pending or 0.00),
        'available_balance': float(wallet_obj.balance_sar or 0.00),
        'total_withdrawn': float(wallet_obj.total_withdrawn or 0.00),
        'currency': getattr(wallet_obj, 'default_currency', 'SAR')
    }

    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    search_query = request.args.get('q', '').strip() or request.args.get('search', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = WalletTransaction.query.filter_by(wallet_id=wallet_obj.id)

    if status_filter == 'all':
        query = query.filter(WalletTransaction.status != 'pending')
    else:
        query = query.filter(WalletTransaction.status == status_filter)

    if type_filter and type_filter != 'all':
        query = query.filter(WalletTransaction.trans_type == type_filter)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                WalletTransaction.reference_number.ilike(search_term),
                WalletTransaction.description.ilike(search_term),
                WalletTransaction.transfer_number.ilike(search_term)
            )
        )

    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WalletTransaction.created_at >= parsed_start)
        except ValueError:
            pass

    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(WalletTransaction.created_at <= parsed_end)
        except ValueError:
            pass

    raw_transactions = query.order_by(WalletTransaction.created_at.desc()).all()
    
    # تجهيز المعاملات لصفحة الطباعة أيضاً
    transactions = []
    for tx in raw_transactions:
        tx.display_bank = getattr(tx, 'bank_name', None) or 'غير محدد'
        tx.display_beneficiary = getattr(tx, 'beneficiary_name', None) or 'غير محدد'
        transactions.append(tx)

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
