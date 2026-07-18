# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

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
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', '').strip()
    
    # تحسين: نرسل قيم فارغة للـ title إذا لم يكن هناك بحث لضمان جلب القائمة كاملة
    variables = {
        "input": {
            "page": page,
            "limit": 100,
            "title": search if search else None
        }
    }
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        if response and 'findAllProducts' in response:
            result = response['findAllProducts']
            # جلب البيانات مباشرة من السيرفر
            products = result.get('data', []) or []
            pagination = result.get('pagination', {"currentPage": page, "totalPages": 1})
            
            # إذا كان هناك بحث، نطبق الفلترة على النتائج القادمة من السيرفر
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
