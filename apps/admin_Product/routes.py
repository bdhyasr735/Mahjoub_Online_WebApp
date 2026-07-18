# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

# استعلام جلب المنتجات
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
    
    # تحسين المتغيرات
    variables = {
        "input": {
            "page": page,
            "limit": 50,
            "title": search if search else ""  # تغيير None إلى "" قد يحسن التوافق مع بعض السيرفرات
        }
    }
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        # تصحيح مسار البيانات
        if response and 'findAllProducts' in response:
            result = response.get('findAllProducts', {})
            
            # جلب البيانات والتأكد من وجودها
            products = result.get('data') if result.get('data') is not None else []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
            
            # في حال عدم وجود بحث، سنعرض المنتجات كما هي
            # في حال وجود بحث، الفلترة التالية تضمن ظهور النتائج حتى لو لم يفلترها السيرفر
            if search:
                products = [
                    p for p in products 
                    if p.get('title') and search.lower() in str(p.get('title')).lower()
                ]
                
        # تسجيل الحالة في التيرمينال للتصحيح
        print(f"DEBUG: Fetched {len(products)} products for title='{search}'")
            
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب البيانات: {e}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search
    )
