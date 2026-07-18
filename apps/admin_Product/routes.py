# coding: utf-8
import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient

logger = logging.getLogger(__name__)
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    # استعلام API يدعم البحث والترقيم
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data { qid, title, quantity, pricing { price }, images { fileUrl }, identification { sku } }
        pagination { totalPages, currentPage, totalItems }
      }
    }
    """
    # نمرر البحث كمتغير للـ API
    variables = {"input": {"page": page, "limit": 20, "search": search} if search else {"page": page, "limit": 20}}
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables) or {}
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        result = {}

    data = result.get('findAllProducts', {})
    products = data.get('data', [])
    pag_info = data.get('pagination', {"totalPages": 1, "currentPage": 1, "totalItems": 0})
    
    # كلاس الموك ليتوافق مع القالب الحالي
    class MockPagination:
        def __init__(self, p):
            self.page = p['currentPage']
            self.pages = p['totalPages']
            self.has_prev = lambda: self.page > 1
            self.has_next = lambda: self.page < self.pages
            self.prev_num = lambda: self.page - 1
            self.next_num = lambda: self.page + 1
            
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=MockPagination(pag_info),
                           search=search)

@admin_product_bp.route('/edit/<qid>', methods=['GET'])
@login_required
def edit_product(qid):
    # جلب المنتج من الـ API مباشرة باستخدام qid
    query = """
    query GetProduct($qid: String!) {
      findProductByQid(qid: $qid) {
        qid, title, quantity, pricing { price }, description, images { fileUrl }
      }
    }
    """
    result = QomrahGraphQLClient.execute_query(query, variables={"qid": qid})
    product = result.get('findProductByQid') if result else None
    
    if not product:
        return "المنتج غير موجود", 404
        
    return render_template('admin/admin_add_product.html', product=product)

# ... (دالة proxy_sync تبقى كما هي للمزامنة الخلفية)
