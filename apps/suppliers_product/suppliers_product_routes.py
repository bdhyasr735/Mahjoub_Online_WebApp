# coding: utf-8
# 📂 apps/suppliers_product/routes.py

from flask import Blueprint, render_template, request, session, abort, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.suppliers_product.services import supplier_product, get_product_stats
from apps.suppliers_product.helpers import paginate, filter_by_search, filter_by_status
import logging

logger = logging.getLogger(__name__)

# ====== BLUEPRINTS ======
bp = Blueprint('suppliers_product_bp', __name__, template_folder='templates')
add_bp = Blueprint('add_product_bp', __name__, template_folder='templates')
edit_bp = Blueprint('edit_product_bp', __name__, template_folder='templates')


def _get_supplier_id():
    return current_user.supplier_id if session.get('user_type') == 'staff' else current_user.id


def _check_access():
    if session.get('user_type') not in ['supplier', 'staff']:
        abort(403)


# ============================================
# 📦 قائمة المنتجات (الروت المرتبط بالواجهة الرئيسية)
# ============================================

@bp.route('/products')
@login_required
def products():
    _check_access()
    try:
        supplier_id = _get_supplier_id()
        search = request.args.get('search', '').strip()
        filter_status = request.args.get('filter', 'all')
        page = request.args.get('page', 1, type=int)
        
        products_list = []
        for m in supplier_product.get_supplier_mappings(supplier_id):
            p = supplier_product.fetch_product_by_qid(m['qid'])
            if p:
                products_list.append({
                    'qid': m['qid'], 
                    'title': p.get('name') or p.get('title') or 'منتج بدون اسم', 
                    'product': p, 
                    'mapping': m
                })
        
        products_list = filter_by_search(products_list, search, 'title')
        if filter_status != 'all':
            products_list = filter_by_status(products_list, filter_status)
        
        paginated = paginate(products_list, page)
        stats = get_product_stats(supplier_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('suppliers/includes/_table_products.html', products=paginated, pagination=paginated)
        
        return render_template('suppliers/suppliers_product.html',
            products=paginated, pagination=paginated, suppliers=supplier_product.get_active_suppliers(),
            total_products=stats['total'], active_products=stats['published'],
            draft_products=stats['draft'], total_suppliers=len(supplier_product.get_active_suppliers()),
            search_query=search, filter_status=filter_status
        )
    except Exception as e:
        logger.error(f"❌ products: {e}")
        return render_template('suppliers/suppliers_product.html', products={'items': [], 'total': 0})
