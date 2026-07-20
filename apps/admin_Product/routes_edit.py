# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

import json
import logging
import urllib.parse
from flask import render_template, request, jsonify, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

logger = logging.getLogger(__name__)

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
            supplier_id
            sku
            weight
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
            variants {
                name
                price
                quantity
                sku
            }
        }
    }  
}
"""

GET_ALL_COLLECTIONS_QUERY = """
query GetAllCollections {
    findAllCollections(input: { limit: 100 }) {
        data { qid title }
    }
}
"""

GET_ALL_SUPPLIERS_QUERY = """
query GetAllSuppliers {
    findAllSuppliers(input: { limit: 200 }) {
        data {
            id
            trade_name
            code
            supplier_code
        }
    }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل منتج موجود بالاعتماد على معرفه (qid) مع جلب الموردين والتصنيفات بصورة آمنة."""
    
    decoded_qid = urllib.parse.unquote(qid)
    
    default_product = {
        "qid": decoded_qid,
        "title": "",
        "slug": "",
        "description": "",
        "status": "ACTIVE",
        "quantity": 0,
        "supplier_id": "",
        "sku": "",
        "weight": 0,
        "pricing": {"price": 0, "originalPrice": 0, "compareAtPrice": 0},
        "images": [],
        "collections": [],
        "collection_ids": [],
        "variants": []
    }
    
    product = default_product
    all_collections = []
    suppliers = []

    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": decoded_qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        sup_response = QomrahGraphQLClient.execute_query(GET_ALL_SUPPLIERS_QUERY)

        # 1. استخراج ومعالجة بيانات المنتج
        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res and find_res.get('data'):
                product = find_res.get('data')

        if product:
            # تنظيف ومعالجة الصور لتتوافق مع القالب
            raw_images = product.get('images') or []
            product['images'] = [img.get('fileUrl') for img in raw_images if isinstance(img, dict) and img.get('fileUrl')]
            
            # استخراج معرفات التصنيفات (QIDs) للمطابقة في القائمة المنسدلة
            raw_collections = product.get('collections') or []
            product['collection_ids'] = [c['qid'] for c in raw_collections if isinstance(c, dict) and c.get('qid')]
            
            # حماية كائن الأسعار
            if not product.get('pricing'):
                product['pricing'] = {"price": 0, "originalPrice": 0, "compareAtPrice": 0}
            
            if not product.get('variants'):
                product['variants'] = []

        # 2. استخراج المجموعات
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', []) or []

        # 3. استخراج الموردين
        if sup_response and 'data' in sup_response:
            suppliers = sup_response['data'].get('findAllSuppliers', {}).get('data', []) or []

    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل {decoded_qid}: {str(e)}", exc_info=True)
        flash("تعذر تحميل بيانات المنتج أو القوائم المرتبطة.", "danger")

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        suppliers=suppliers,
        all_collections=all_collections
    )
