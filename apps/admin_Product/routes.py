# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash
from flask_login import login_required
from apps.admin_Product import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

# استعلام جلب المنتجات من واجهة قمرة
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
    
    # رفع حد الجلب لـ 100 منتج لضمان كفاءة الفلترة النصية المحلية لـ (title)
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
            all_products = result.get('data', []) or []
            
            # محاكاة لعملية الفلترة النصية المتقدمة CONTAINS يدوياً في بايثون
            if search:
                products = [
                    p for p in all_products 
                    if p.get('title') and search.lower() in str(p.get('title')).lower()
                ]
                # عند البحث المحلي نثبت الترقيم في صفحة واحدة للمخرجات المفلترة
                pagination = {"currentPage": 1, "totalPages": 1}
            else:
                products = all_products
                pagination = result.get('pagination', {"currentPage": page, "totalPages": 1})
                
    except Exception as e:
        print(f"❌ خطأ في موديول المنتجات: {e}")
        flash("حدث خطأ أثناء معالجة أو جلب البيانات.")

    return render_template(
        'admin/admin_product.html',
        products=products,
        pagination=pagination,
        search=search
    )
