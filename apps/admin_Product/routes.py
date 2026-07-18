# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.admin_Product import admin_product_bp
from apps.services.graphql_client import GraphQLClient

# تعريف الـ Query التي تستخدمها لجلب المنتجات بناءً على الـ Schema الخاصة بك
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
    
    # تجهيز متغيرات الطلب (يجب أن يتطابق 'title' مع ما يتوقعه السيرفر)
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
        # تنفيذ الطلب الفعلي للسيرفر
        response = GraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        # استخراج البيانات بوضوح لتجنب الأخطاء
        if response and 'data' in response and 'findAllProducts' in response['data']:
            result = response['data']['findAllProducts']
            products = result.get('data', [])
            pagination = result.get('pagination', {"currentPage": page, "totalPages": 1})
            
    except Exception as e:
        # في حالة فشل الاتصال، يتم تمرير قائمة فارغة مع تسجيل الخطأ
        print(f"Error fetching products: {e}")
        flash("حدث خطأ أثناء جلب المنتجات، يرجى المحاولة لاحقاً.")

    return render_template(
        'admin/admin_product.html',
        products=products,
        pagination=pagination,
        search=search
    )

@admin_product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    return render_template('admin/add_product.html')

@admin_product_bp.route('/edit/<qid>', methods=['GET', 'POST'])
@login_required
def edit_product(qid):
    return render_template('admin/edit_product.html', qid=qid)
