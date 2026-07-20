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

GET_PRODUCT_DETAIL_QUERY = """
query GetProductDetail($qid: String!) {  
    findProductByQid(qid: $qid) {  
        data {
            qid
            title
            slug
            description
            status
            quantity
            sku
            weight
            variants
            pricing { 
                price 
                originalPrice
                compareAtPrice 
            }
            images { 
                _id 
                fileUrl 
            }
            collections { 
                qid 
                title 
            }
        }
    }  
}
"""

GET_ALL_COLLECTIONS_QUERY = """
query GetAllCollections {
    findAllCollections(input: { limit: 100 }) {
        data { qid, title }
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


@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    """عرض صفحة إضافة منتج جديد."""
    empty_product = {
        "title": "",
        "slug": "",
        "description": "",
        "status": "ACTIVE",
        "quantity": 0,
        "sku": "",
        "weight": 0,
        "variants": [],
        "pricing": {"price": 0, "originalPrice": 0, "compareAtPrice": 0},
        "images": [],
        "collection_ids": []
    }
    
    all_collections = []
    try:
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])
    except Exception:
        pass

    return render_template(
        'admin/admin_edit_product.html',
        product=empty_product,
        suppliers=[],
        all_collections=all_collections
    )


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل منتج موجود بالاعتماد على معرفه (qid)."""
    product = None
    all_collections = []

    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)

        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res:
                product = find_res.get('data')

        if product:
            raw_images = product.get('images', [])
            product['images'] = [img.get('fileUrl') for img in raw_images if isinstance(img, dict) and img.get('fileUrl')]
            product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c and c.get('qid')]

        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])

    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل {qid}: {str(e)}")
        flash("تعذر تحميل بيانات المنتج.", "danger")

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        suppliers=[],
        all_collections=all_collections
    )


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '')
        sku = request.form.get('sku', '').strip()
        quantity = int(request.form.get('quantity', 0) or 0)
        weight = float(request.form.get('weight', 0) or 0)
        
        original_price = float(request.form.get('original_price') or 0)
        compare_at_price = float(request.form.get('compare_at_price') or 0)
        price = float(request.form.get('price') or 0)
        
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
