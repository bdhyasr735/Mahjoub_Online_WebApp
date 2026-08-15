from flask import Blueprint, render_template, request, jsonify, redirect, url_for

bp = Blueprint('suppliers_wallets_controller', __name__)

PER_PAGE = 10

@bp.route('/', methods=['GET'])
def index():
    """
    الصفحة الرئيسية للوحة تحكم محافظ الموردين
    عرض المؤشرات المالية، البحث، وجدول المحافظ مع الترقيم
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    bank_filter = request.args.get('bank', 'all', type=str)
    
    kpis = {
        'total_wallets_balance': 3828900.50,
        'total_available_payouts': 3012000.00,
        'total_escrow_held': 816900.50,
        'total_suppliers_count': 1420850,
        'active_suppliers_count': 10,
        'pending_withdrawals_amount': 345800.00,
        'pending_withdrawals_count': 28
    }

    total_records = 10
    total_pages = max(1, (total_records + PER_PAGE - 1) // PER_PAGE)
    
    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'prev_page': max(1, page - 1),
        'next_page': min(total_pages, page + 1),
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'per_page': PER_PAGE,
        'total_count': total_records
    }

    suppliers = get_suppliers_list(search=search_query, status=status_filter, bank=bank_filter, page=page, per_page=PER_PAGE)

    return render_template(
        'admin/suppliers_wallets.html',
        kpis=kpis,
        pagination=pagination,
        suppliers=suppliers,
        search_query=search_query,
        status_filter=status_filter,
        bank_filter=bank_filter
    )

@bp.route('/<supplier_id>', methods=['GET'])
def supplier_ledger_detail(supplier_id):
    """
    صفحة كشف الحساب والعمليات الدفترية الفردية للمورد
    """
    wallet = get_supplier_wallet_by_id(supplier_id)
    if not wallet:
        return render_template('admin/404.html'), 404
        
    return render_template(
        'admin/supplier_ledger_detail.html',
        wallet=wallet
    )

def get_suppliers_list(search='', status='all', bank='all', page=1, per_page=10):
    return []

def get_supplier_wallet_by_id(supplier_id):
    return {}
