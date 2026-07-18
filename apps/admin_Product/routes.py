# coding: utf-8
import logging
from flask import render_template, request
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
from .registry import admin_product_bp

logger = logging.getLogger(__name__)

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    # 1. استخراج المتغيرات من رابط الـ URL
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    # 2. استعلام GraphQL
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data { 
            qid, title, quantity, 
            pricing { price }, 
            identification { sku },
            images { fileUrl } 
        }
        pagination { totalPages, currentPage, totalItems }
      }
    }
    """
    
    # تصحيح مفتاح البحث ليكون 'title'
    variables = {
        "input": {
            "page": page, 
            "limit": 100,
            "title": search if search else None
        }
    }
    
    # 3. تنفيذ الاستعلام مع تتبع المتغيرات في السجلات
    logger.info(f"DEBUG: Variables sent to GraphQL: {variables}")
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables) or {}
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        result = {}

    # 4. معالجة البيانات القادمة من السيرفر
    data_payload = result.get('findAllProducts', {})
    products = data_payload.get('data', [])
    pag_info = data_payload.get('pagination', {"totalPages": 1, "currentPage": 1, "totalItems": 0})
    
    class Pagination:
        def __init__(self, p):
            self.currentPage = p.get('currentPage', 1)
            self.totalPages = p.get('totalPages', 1)
            self.totalItems = p.get('totalItems', 0)
    
    return render_template(
        'admin/admin_Product.html', 
        products=products, 
        pagination=Pagination(pag_info),
        search=search
    )
