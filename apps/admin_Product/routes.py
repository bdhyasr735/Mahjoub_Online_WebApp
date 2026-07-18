# coding: utf-8
from flask import render_template, request, flash
from flask_login import login_required
from apps.admin_Product import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

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
    # استخدام .get للحصول على القيمة وضمان عدم ضياعها
    search = request.args.get('title', '').strip()
    
    variables = {
        "input": {
            "page": page,
            "limit": 20,
            "title": search if search else None
        }
    }
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        if response and 'findAllProducts' in response:
            result = response['findAllProducts']
            products = result.get('data', [])
            pagination = result.get('pagination', {"currentPage": page, "totalPages": 1})
    except Exception as e:
        print(f"Error: {e}")
        flash("حدث خطأ أثناء جلب البيانات.")

    return render_template(
        'admin/admin_product.html',
        products=products,
        pagination=pagination,
        search=search
    )
