# coding: utf-8
# 📂 apps/admin_Product/routes_display.py

import logging
from flask import render_template, request, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

logger = logging.getLogger(__name__)

GET_ALL_PRODUCTS_QUERY = """
query Data($input: GetAllProductsInput) {
    findAllProducts(input: $input) {
        data {
            qid
            title
            pricing { price }
            quantity
            images { fileUrl }
        }
        pagination { currentPage, totalPages }
    }
}
"""

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """راوتر واجهة العرض: يجلب فقط الحقول البسيطة والأساسية الظاهرة في شبكة المنتجات."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', '').strip()
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        input_data = {"page": page, "limit": 50}
        if search:
            input_data["title"] = search
            
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, {"input": input_data})
        if response and 'data' in response:
            result = response['data'].get('findAllProducts', {})
            products = result.get('data') or []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
    except Exception as e:
        logger.error(f"❌ خطأ في جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    return render_template('admin/admin_Product.html', products=products, pagination=pagination, search=search)
