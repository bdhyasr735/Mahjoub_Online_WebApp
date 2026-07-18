# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, flash, jsonify
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

# استعلام جلب منتج واحد للتعديل
GET_PRODUCT_QUERY = """
query GetProduct($qid: ID!) {
  findProduct(qid: $qid) {
    qid
    title
    pricing { price }
    quantity
    images { fileUrl }
  }
}
"""

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
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
        if response and 'findAllProducts' in response:
            result = response.get('findAllProducts', {})
            products = result.get('data') if result.get('data') is not None else []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
            
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

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل المنتج"""
    try:
        response = QomrahGraphQLClient.execute_query(GET_PRODUCT_QUERY, {"qid": qid})
        product = response.get('findProduct', {})
        return render_template('admin/admin_edit_product.html', product=product)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج: {e}")
        flash("فشل تحميل بيانات المنتج للتعديل.")
        return render_template('admin/admin_edit_product.html', product={})

@admin_product_bp.route('/update_product', methods=['POST'])
@login_required
def update_product():
    """استقبال طلب تحديث المنتج من واجهة المستخدم"""
    data = request.json
    try:
        # هنا ستضع الـ Mutation الخاص بـ QomrahGraphQLClient.execute_query(...)
        # لتحديث المنتج في قاعدة البيانات
        logger.info(f"🔄 جاري تحديث المنتج: {data.get('qid')}")
        
        # عند اكتمال التحديث بنجاح من الـ API:
        return jsonify({"status": "success", "message": "تم تحديث المنتج بنجاح"})
    except Exception as e:
        logger.error(f"❌ خطأ أثناء التحديث: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
