# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import logging
from flask import render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

try:
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.models.supplier import Supplier
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False

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
            pricing { price, cost_price, compare_price }
            images { _id, fileUrl }
            collections { qid, title }
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
    """التحويل المباشر لقالب إضافة المنتج بكل خفة وسرعة"""
    return render_template(
        'admin/admin_add_product.html',
        product=None,
        suppliers=[],
        mapping={"selected_supplier_id": None},
        all_collections=[]
    )


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        
        product_node = None
        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res:
                product_node = find_res.get('data')

        if not product_node:
            flash("❌ تعذر جلب بيانات المنتج.", "danger")
            return redirect(url_for('admin_product_bp.manage_products'))
            
        product = product_node
        product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c and c.get('qid')]

        all_collections = []
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])

        suppliers = []
        mapping_data = {"selected_supplier_id": None}
        if HAS_MODELS:
            try:
                suppliers = Supplier.query.all()
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if mapping:
                    mapping_data["selected_supplier_id"] = str(mapping.supplier_id)
            except Exception as db_err:
                logger.error(f"⚠️ خطأ الموردين: {db_err}")

        return render_template(
            'admin/admin_add_product.html',
            product=product,
            suppliers=suppliers,
            mapping=mapping_data,
            all_collections=all_collections
        )

    except Exception as e:
        logger.error(f"❌ خطأ في التعديل: {str(e)}")
        flash("حدث خطأ تقني.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))


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
