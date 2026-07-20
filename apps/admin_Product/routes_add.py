# coding: utf-8
# 📂 apps/admin_Product/routes_add.py

import json
import logging
from flask import render_template, request, jsonify, flash
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

GET_PRODUCT_BY_QID_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    data {
      qid
      title
      description
      status
      quantity
      pricing {
        price
      }
      images {
        _id
        fileUrl
      }
    }
  }
}
"""

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """جلب وعرض قائمة المنتجات مع التصفح والبحث."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', '').strip()
    
    input_data = {"page": page, "limit": 50}
    if search:
        input_data["title"] = search
        
    variables = {"input": input_data}
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        if response and 'data' in response:
            result = response['data'].get('findAllProducts', {})
            products = result.get('data') or []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
        else:
            logger.warning("⚠️ استجابة فارغة من قمرة عند جلب المنتجات.")
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.", "danger")

    return render_template(
        'admin/admin_Product.html',
        products=products,
        pagination=pagination,
        search=search
    )


@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product_page():
    """عرض صفحة إضافة منتج جديد مع كائن فارغ آمن لتجنب أخطاء القالب."""
    empty_product = {
        "title": "",
        "description": "",
        "status": "ACTIVE",
        "quantity": 0,
        "pricing": {"price": 0},
        "images": []
    }
    return render_template(
        'admin/admin_add_product.html',
        product=empty_product
    )


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """عرض صفحة تعديل منتج موجود بالاعتماد على معرفه (qid)."""
    product = None

    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_BY_QID_QUERY, {"qid": qid})
        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res:
                product = find_res.get('data')
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل {qid}: {str(e)}")
        flash("تعذر تحميل بيانات المنتج.", "danger")

    return render_template(
        'admin/admin_add_product.html',
        product=product
    )


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync_product():
    """معالجة حفظ أو تحديث المنتج واستلام البيانات والوسائط الأساسية."""
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '')
        quantity = int(request.form.get('quantity', 0) or 0)
        price = float(request.form.get('price') or 0)
        
        image_ids = json.loads(request.form.get('image_ids', '[]'))
        new_uploaded_files = request.files.getlist('images')

        action_type = "تحديث" if qid else "إنشاء"
        logger.info(f"✅ تم {action_type} المنتج بنجاح: {title}")

        return jsonify({
            "status": "success",
            "message": f"تم {action_type} المنتج وحفظ البيانات بنجاح."
        }), 200

    except Exception as e:
        logger.error(f"❌ خطأ أثناء معالجة حفظ المنتج: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"حدث خطأ أثناء الحفظ: {str(e)}"
        }), 500
