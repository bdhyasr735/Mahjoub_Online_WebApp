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

# --- 🔍 1. الاستعلامات (Queries) ---

GET_ALL_PRODUCTS_QUERY = """
query GetAllProducts($input: GetAllProductsInput) {
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
        qid
        title
        slug
        description
        status
        quantity
        sku
        weight
        supplier_id
        collection_ids
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
        variants {
            name
            price
            quantity
            sku
        }
        collections { 
            qid 
            title 
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

GET_ALL_SUPPLIERS_QUERY = """
query GetAllSuppliers {
    findAllSuppliers(input: { limit: 100 }) {
        data { id, trade_name, supplier_code }
    }
}
"""

# --- ✏️ 2. المتحولات (Mutations) ---

CREATE_PRODUCT_MUTATION = """
mutation CreateProduct($input: CreateProductInput!) {
    createProduct(input: $input) { qid }
}
"""

UPDATE_PRODUCT_MUTATION = """
mutation UpdateProduct($qid: ID!, $input: UpdateProductInput!) {
    updateProduct(qid: $qid, input: $input) { qid }
}
"""


# --- 🌐 3. المسارات (Routes) ---

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """عرض جدول إدارة المنتجات مع البحث والصفحات."""
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
            result = response['data'].get('findAllProducts', {}) or {}
            products = result.get('data') or []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
    except Exception as e:
        logger.error(f"❌ خطأ في جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.", "danger")

    return render_template(
        'admin/admin_Product.html', 
        products=products, 
        pagination=pagination, 
        search=search
    )


@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    """عرض صفحة إضافة منتج جديد."""
    empty_product = {
        "title": "", "slug": "", "description": "", "status": "ACTIVE",
        "quantity": 0, "sku": "", "weight": 0,
        "pricing": {"price": 0, "originalPrice": 0, "compareAtPrice": 0, "costPrice": 0},
        "images": [], "collection_ids": [], "supplier_id": "", "variants": []
    }
    
    all_collections = []
    suppliers = []

    try:
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب المجموعات لصفحة الإضافة: {str(e)}")

    try:
        sup_response = QomrahGraphQLClient.execute_query(GET_ALL_SUPPLIERS_QUERY)
        if sup_response and 'data' in sup_response:
            suppliers = sup_response['data'].get('findAllSuppliers', {}).get('data', [])
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب الموردين لصفحة الإضافة: {str(e)}")

    return render_template(
        'admin/admin_add_product.html', 
        product=empty_product, 
        all_collections=all_collections,
        suppliers=suppliers
    )


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل منتج قائم مع جلب بياناته وبيانات المجموعات والموردين."""
    decoded_qid = urllib.parse.unquote(qid)
    product = None
    all_collections = []
    suppliers = []

    try:
        # جلب تفاصيل المنتج
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": decoded_qid})
        if prod_response and 'data' in prod_response:
            product = prod_response['data'].get('findProductByQid')
            if product:
                # معالجة تنسيق الصور وتحديد معرفات المجموعات
                raw_images = product.get('images', [])
                product['images'] = [
                    img.get('fileUrl') if isinstance(img, dict) else img 
                    for img in raw_images
                ]
                if 'collections' in product and not product.get('collection_ids'):
                    product['collection_ids'] = [
                        c['qid'] for c in product.get('collections', []) if isinstance(c, dict) and c.get('qid')
                    ]

        # جلب المجموعات
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])

        # جلب الموردين
        sup_response = QomrahGraphQLClient.execute_query(GET_ALL_SUPPLIERS_QUERY)
        if sup_response and 'data' in sup_response:
            suppliers = sup_response['data'].get('findAllSuppliers', {}).get('data', [])

    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل ({decoded_qid}): {str(e)}")
        flash("تعذر تحميل بيانات المنتج.", "danger")

    return render_template(
        'admin/admin_edit_product.html', 
        product=product, 
        all_collections=all_collections,
        suppliers=suppliers
    )


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync_product():
    """معالجة حفظ وإنشاء أو تحديث المنتج ومزامنة البيانات والوسائط عبر GraphQL."""
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        description = request.form.get('description', '')
        status = request.form.get('status', 'ACTIVE').strip()
        quantity = int(request.form.get('quantity', 0) or 0)
        weight = float(request.form.get('weight', 0) or 0)
        sku = request.form.get('sku', '').strip()
        
        cost_price = float(request.form.get('original_price', 0) or 0)
        compare_price = float(request.form.get('compare_at_price', 0) or 0)
        price = float(request.form.get('price', 0) or 0)
        
        supplier_id = request.form.get('supplier_id', '').strip()
        collection_ids = json.loads(request.form.get('collection_ids', '[]'))
        variants = json.loads(request.form.get('variants', '[]'))
        removed_images = json.loads(request.form.get('removed_images', '[]'))

        # تجهيز كائن البيانات المرفوع للـ GraphQL
        input_payload = {
            "title": title,
            "slug": slug,
            "description": description,
            "status": status,
            "quantity": quantity,
            "weight": weight,
            "sku": sku,
            "supplierId": supplier_id if supplier_id else None,
            "collectionIds": collection_ids,
            "pricing": {
                "price": price,
                "originalPrice": cost_price,
                "compareAtPrice": compare_price
            },
            "variants": variants
        }

        if qid:
            # 🔄 تحديث منتج قائم
            input_payload["removedImages"] = removed_images
            response = QomrahGraphQLClient.execute_mutation(
                UPDATE_PRODUCT_MUTATION, 
                {"qid": qid, "input": input_payload}
            )
            action_msg = "تم تحديث المنتج ومزامنة البيانات بنجاح."
        else:
            # ➕ إنشاء منتج جديد
            response = QomrahGraphQLClient.execute_mutation(
                CREATE_PRODUCT_MUTATION, 
                {"input": input_payload}
            )
            action_msg = "تم إنشاء المنتج وحفظه بنجاح."

        if response and 'errors' in response:
            error_msg = response['errors'][0]['message']
            return jsonify({"status": "error", "message": f"خطأ في الـ API: {error_msg}"}), 400

        return jsonify({"status": "success", "message": action_msg}), 200

    except Exception as e:
        logger.error(f"❌ خطأ أثناء حفظ ومزامنة المنتج: {str(e)}")
        return jsonify({"status": "error", "message": f"حدث خطأ أثناء الحفظ: {str(e)}"}), 400
