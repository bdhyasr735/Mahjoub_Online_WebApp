# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

# استعلام جلب كل المنتجات
GET_ALL_PRODUCTS_QUERY = """
query Data($input: GetAllProductsInput) {
  findAllProducts(input: $input) {
    data {
      qid
      title
      pricing { price }
      quantity
      identification { sku }  # أضفت هذا الحقل لدعم عرض الـ SKU في الجدول
      images { fileUrl }
    }
    pagination { currentPage, totalPages }
  }
}
"""

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """جلب وعرض قائمة المنتجات مع دعم البحث والترقيم"""
    page = request.args.get('page', 1, type=int)
    # نوحد الاسم ليكون search في الكود والقالب
    search = request.args.get('search', '').strip()
    
    # إعداد المتغيرات للاستعلام
    input_data = {"page": page, "limit": 50}
    if search:
        input_data["title"] = search
        
    variables = {"input": input_data}
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        # التأكد من وصول البيانات وتنسيقها
        if response and 'data' in response:
            result = response['data'].get('findAllProducts', {})
            products = result.get('data') or []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
        else:
            logger.warning(f"⚠️ استجابة فارغة من قمرة عند جلب المنتجات.")
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    # إرجاع القالب مع البيانات
    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search # يتم تمريره للقالب ليبقى في حقل البحث
    )
