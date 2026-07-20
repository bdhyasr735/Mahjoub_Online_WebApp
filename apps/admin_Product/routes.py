# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import logging
import urllib.parse
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
            pricing { 
                price 
                originalPrice 
                compareAtPrice 
                costPrice
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
    """راوتر واجهة عرض المنتجات والبحث والتنقل بين الصفحات."""
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
        logger.error(f"❌ خطأ في جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    return render_template('admin/admin_Product.html', products=products, pagination=pagination, search=search)


@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    """عرض صفحة إضافة منتج جديد مع كائن فارغ وقوائم المجموعات."""
    empty_product = {
        "title": "",
        "slug": "",
        "description": "",
        "status": "ACTIVE",
        "quantity": 0,
        "sku": "",
        "weight": 0,
        "variants": [],
        "pricing": {"price": 0, "originalPrice": 0, "compareAtPrice": 0, "costPrice": 0},
        "images": [],
        "collection_ids": []
    }
    
    all_collections = []
    try:
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب المجموعات لصفحة الإضافة: {str(e)}")

    return render_template(
        'admin/admin_add_product.html',
        product=empty_product,
        suppliers=[],
        all_collections=all_collections
    )


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل منتج موجود بالاعتماد على معرفه (qid) مع فك التشفير المناسب."""
    # فك تشفير الـ qid لتجنب مشاكل الأحرف الخاصة والمسارات المزدوجة
    decoded_qid = urllib.parse.unquote(qid)
    
    product = {
        "qid": decoded_qid,
        "title": "",
        "slug": "",
        "description": "",
        "status": "ACTIVE",
        "quantity": 0,
        "sku": "",
        "weight": 0,
        "variants": [],
        "pricing": {"price": 0, "originalPrice": 0, "compareAtPrice": 0, "costPrice": 0},
        "images": [],
        "collection_ids": []
    }
    all_collections = []

    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": decoded_qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)

        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res and find_res.get('data'):
                product = find_res.get('data')

        if product:
            raw_images = product.get('images', [])
            product['images'] = [img.get('fileUrl') for img in raw_images if isinstance(img, dict) and img.get('fileUrl')]
            product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c and c.get('qid')]
            
            # التأكد من وجود كائن pricing لتجنب أي أخطاء في القالب
            if not product.get('pricing'):
                product['pricing'] = {"price": 0, "originalPrice": 0, "compareAtPrice": 0, "costPrice": 0}

        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])

    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل {decoded_qid}: {str(e)}")
        flash("تعذر تحميل بيانات المنتج.", "danger")

    return render_template(
        'admin/admin_add_product.html',
        product=product,
        suppliers=[],
        all_collections=all_collections
    )


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """معالجة حفظ وإنشاء أو تحديث المنتج واستلام البيانات والوسائط."""
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '')
        sku = request.form.get('sku', '').strip()
        quantity = int(request.form.get('quantity', 0) or 0)
        weight = float(request.form.get('weight', 0) or 0)
        
        price = float(request.form.get('price') or 0)
        
        supplier_id = request.form.get('supplier_id', '')
        collections = json.loads(request.form.get('collection_ids', '[]'))
        variants = request.form.get('variants', '[]')
        
        uploaded_images = request.files.getlist('images')

        action_type = "تحديث" if qid else "إنشاء"
        logger.info(f"✅ تم {action_type} المنتج بنجاح: {title} [عدد الصور المرفوعة: {len(uploaded_images)}]")

        return jsonify({
            "status": "success",
            "message": f"تم {action_type} المنتج وحفظ البيانات بنجاح."
        }), 200

    except Exception as e:
        logger.error(f"❌ خطأ أثناء معالجة حفظ المنتج: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"حدث خطأ أثناء الحفظ: {str(e)}"
        }), 400
