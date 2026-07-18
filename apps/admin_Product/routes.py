# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

# استعلام جلب المنتجات (عرض فقط)
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
    """عرض قائمة المنتجات مع دعم البحث والترقيم"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', '').strip()
    
    variables = {
        "input": {
            "page": page,
            "limit": 50,
            "title": search if search else "" 
        }
    }
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        # التأكد من هيكلية الاستجابة من قمرة
        if response and 'data' in response and 'findAllProducts' in response['data']:
            result = response['data']['findAllProducts']
            products = result.get('data') if result.get('data') is not None else []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
            
            # فلترة إضافية محلية في حال لزم الأمر لضمان تطابق النتائج مع البحث
            if search:
                products = [
                    p for p in products 
                    if p.get('title') and search.lower() in str(p.get('title')).lower()
                ]
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب البيانات: {e}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search
    )
