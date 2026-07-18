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
    
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data { qid, title, quantity, pricing { price }, images { fileUrl }, identification { sku } }
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
    
    # كلاس ترقيم احترافي لإظهار كافة التفاصيل
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

@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    return render_template('admin/admin_add_product.html', product=None)

@admin_product_bp.route('/edit/<qid>', methods=['GET'])
@login_required
def edit_product(qid):
    query = """
    query GetProduct($qid: String!) {
      findProductByQid(qid: $qid) {
        qid, title, quantity, pricing { price }, identification { sku }, images { fileUrl }
      }
    }
    """
    result = QomrahGraphQLClient.execute_query(query, variables={"qid": qid})
    product = result.get('findProductByQid') if result else None
    
    if not product:
        return "المنتج غير موجود", 404
        
    return render_template('admin/admin_add_product.html', product=product)

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    data = request.json
    mutation = """
    mutation UpdateProduct($input: UpdateProductInput!) {
        updateProduct(input: $input) { qid }
    }
    """
    variables = {
        "input": {
            "title": data.get('title'),
            "price": float(data.get('price', 0)),
            "quantity": int(data.get('quantity', 0)),
            "sku": data.get('sku'),
            "imageUrl": data.get('imageUrl')
        }
    }
    result = QomrahGraphQLClient.execute_query(mutation, variables=variables)
    return jsonify({"status": "success"}) if result else jsonify({"status": "error"}), 200

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    return jsonify({"status": "success", "message": "تمت المزامنة"})
