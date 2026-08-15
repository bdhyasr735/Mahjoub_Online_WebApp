from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from apps.admin_suppliers_wallets.models.wallet_model import SupplierWallet, WalletLedgerEntry, db
from sqlalchemy import or_, func

bp = Blueprint('suppliers_wallets_controller', __name__)

PER_PAGE = 10

@bp.route('/', methods=['GET'])
def index():
    """
    الصفحة الرئيسية للوحة تحكم محافظ الموردين
    عرض المؤشرات المالية الحقيقية، البحث، وجدول المحافظ مع الترقيم القائم على قاعدة البيانات
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    bank_filter = request.args.get('bank', 'all', type=str)
    
    # بناء الاستعلام الأساسي للمحافظ
    query = SupplierWallet.query

    # تطبيق البحث النصي (اسم المورد، كود المحفظة، السجل التجاري، الآيبان، أو المدينة)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                SupplierWallet.supplier_name.ilike(search_term),
                SupplierWallet.wallet_code.ilike(search_term),
                SupplierWallet.commercial_register.ilike(search_term),
                SupplierWallet.iban.ilike(search_term),
                SupplierWallet.city.ilike(search_term)
            )
        )

    # فلترة حسب الحالة
    if status_filter and status_filter != 'all':
        query = query.filter(SupplierWallet.status == status_filter)

    # فلترة حسب البنك المعتمد
    if bank_filter and bank_filter != 'all':
        query = query.filter(SupplierWallet.bank_name == bank_filter)

    # حساب المؤشرات المالية الحقيقية (KPIs) من قاعدة البيانات
    total_wallets_balance = db.session.query(func.sum(SupplierWallet.balance)).scalar() or 0.00
    total_available_payouts = db.session.query(func.sum(SupplierWallet.available_balance)).scalar() or 0.00
    total_escrow_held = db.session.query(func.sum(SupplierWallet.escrow_balance)).scalar() or 0.00
    
    total_suppliers_count = SupplierWallet.query.count()
    active_suppliers_count = SupplierWallet.query.filter_by(status='active').count()
    
    # العمليات المعلقة (إن وجدت ضمن جدول الحركات الدفترية أو المحافظ)
    pending_withdrawals_amount = db.session.query(func.sum(WalletLedgerEntry.amount)).filter_by(status='pending').scalar() or 0.00
    pending_withdrawals_count = WalletLedgerEntry.query.filter_by(status='pending').count()

    kpis = {
        'total_wallets_balance': total_wallets_balance,
        'total_available_payouts': total_available_payouts,
        'total_escrow_held': total_escrow_held,
        'total_suppliers_count': total_suppliers_count,
        'active_suppliers_count': active_suppliers_count,
        'pending_withdrawals_amount': pending_withdrawals_amount,
        'pending_withdrawals_count': pending_withdrawals_count
    }

    # تنفيذ الترقيم (Pagination) باستخدام SQLAlchemy Paginate
    pagination_obj = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    suppliers = pagination_obj.items

    pagination = {
        'current_page': pagination_obj.page,
        'total_pages': pagination_obj.pages,
        'prev_page': pagination_obj.prev_num,
        'next_page': pagination_obj.next_num,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'per_page': PER_PAGE,
        'total_count': pagination_obj.total
    }

    return render_template(
        'admin/suppliers_wallets.html',
        kpis=kpis,
        pagination=pagination,
        suppliers=suppliers,
        search_query=search_query,
        status_filter=status_filter,
        bank_filter=bank_filter
    )

@bp.route('/<int:supplier_id>', methods=['GET'])
def supplier_ledger_detail(supplier_id):
    """
    صفحة كشف الحساب والعمليات الدفترية الفردية للمورد من قاعدة البيانات
    """
    wallet = SupplierWallet.query.get_or_404(supplier_id)
        
    return render_template(
        'admin/supplier_ledger_detail.html',
        wallet=wallet
    )
