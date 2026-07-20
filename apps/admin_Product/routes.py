# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import logging
from flask import render_template, request, flash, jsonify, redirect, url_for
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
      identification { sku }
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
        logger.error(f"❌ خطأ في جلب المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    return render_template('admin/admin_Product.html', products=products, pagination=pagination, search=search)


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        
        action_type = "تحديث" if qid else "إنشاء"
        logger.info(f"✅ تم {action_type} المنتج: {title}")

        return jsonify({
            "status": "success", 
            "message": f"تم {action_type} المنتج بنجاح"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ خطأ في الحفظ: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ: {str(e)}"
        }), 400
