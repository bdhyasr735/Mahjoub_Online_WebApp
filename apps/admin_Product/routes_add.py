# coding: utf-8
import logging
from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient

# تعريف الـ Blueprint في ملف الـ routes لضمان توفره للـ registry وللملفات الأخرى
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

logger = logging.getLogger(__name__)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data { qid, title, quantity, pricing { price }, images { fileUrl } }
        pagination { totalPages, currentPage, totalItems }
      }
    }
    """
    variables = {"input": {"page": page, "limit": 20, "search": search} if search else {"page": page, "limit": 20}}
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables) or {}
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        result = {}

    data = result.get('findAllProducts', {})
    products = data.get('data', [])
    pag_info = data.get('pagination', {"totalPages": 1, "currentPage": 1, "totalItems": 0})
    
    class ProPagination:
        def __init__(self, p):
            self.page = p['currentPage']
            self.pages = p['totalPages']
            self.total = p['totalItems']
            self.has_prev = lambda: self.page > 1
            self.has_next = lambda: self.page < self.pages
            self.prev_num = lambda: self.page - 1
            self.next_num = lambda: self.page + 1
            
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=ProPagination(pag_info),
                           search=search)

# استيراد الملفات الفرعية في نهاية الملف لتسجيل الراوترات الخاصة بها في نفس الـ Blueprint
from . import routes_add, routes_edit, routes_sync
