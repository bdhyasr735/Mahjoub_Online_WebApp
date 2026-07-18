# coding: utf-8
import logging
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
from .registry import admin_product_bp

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
    
    variables = {
        "input": {
            "page": page, 
            "limit": 12, 
            "search": search if search else None
        }
    }
    
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
            self.currentPage = p.get('currentPage', 1)
            self.totalPages = p.get('totalPages', 1)
            self.totalItems = p.get('totalItems', 0)
            self.has_prev = self.currentPage > 1
            self.has_next = self.currentPage < self.totalPages
            self.prev_num = self.currentPage - 1
            self.next_num = self.currentPage + 1
            
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=ProPagination(pag_info),
                           search=search)

@admin_product_bp.route('/edit/<qid>', methods=['GET'])
@login_required
def edit_product(qid):
    # جلب تفاصيل منتج واحد باستخدام الـ qid
    query = """
    query GetProduct($qid: String!) {
      getProduct(qid: $qid) {
        qid, title, quantity, pricing { price }, images { fileUrl }
      }
    }
    """
    result = QomrahGraphQLClient.execute_query(query, variables={"qid": qid}) or {}
    product = result.get('getProduct', {})
    return render_template('admin/admin_edit_product.html', product=product)

@admin_product_bp.route('/update_product', methods=['POST'])
@login_required
def update_product():
    data = request.json
    # استدعاء GraphQL للتحديث
    query = """
    mutation UpdateProduct($input: UpdateProductInput!) {
      updateProduct(input: $input) {
        status, message
      }
    }
    """
    try:
        # تأكد من مطابقة مدخلات الـ mutation في السيرفر
        result = QomrahGraphQLClient.execute_query(query, variables={"input": data})
        return jsonify(result.get('updateProduct', {"status": "success", "message": "تم التحديث"}))
    except Exception as e:
        logger.error(f"Update Error: {e}")
        return jsonify({"status": "error", "message": "فشل الاتصال بالسيرفر"})
