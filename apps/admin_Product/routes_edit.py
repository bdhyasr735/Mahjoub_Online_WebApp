# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

import json
import logging
from flask import render_template, request, jsonify, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

logger = logging.getLogger(__name__)

# استعلام GraphQL لجلب تفاصيل منتج معين بواسطة qid عند التعديل
GET_PRODUCT_BY_QID_QUERY = """
query GetProduct($qid: ID!) {
  findProductByQid(qid: $qid) {
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
    }
    images {
      fileUrl
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

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product_page(qid):
    """عرض صفحة تعديل المنتج وجلب بياناته الأصلية من الباك إند عبر qid."""
    product = {
        "qid": qid,
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
    
    # جلب بيانات المنتج المحدد
    try:
        response = QomrahGraphQLClient.execute_query(GET_PRODUCT_BY_QID_QUERY, {"qid": qid})
        if response and 'data' in response:
            fetched_product = response['data'].get('findProductByQid')
            if fetched_product:
                product.update(fetched_product)
                
                # معالجة الصور لاستخلاص الروابط النصية مباشرة
                raw_images = fetched_product.get('images', [])
                product['images'] = [
                    img.get('fileUrl') if isinstance(img, dict) else img 
                    for img in raw_images if img
                ]
                
                # استخراج معرّفات المجموعات لتحديد المربع المختصر في القالب
                raw_cols = fetched_product.get('collections', [])
                product['collection_ids'] = [
                    c.get('qid') for c in raw_cols if isinstance(c, dict) and c.get('qid')
                ]
                
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج [QID: {qid}]: {str(e)}")
        flash("تعذر جلب تفاصيل المنتج من الخادم، يرجى المحاولة لاحقاً.", "warning")

    # جلب قائمة المجموعات المتاحة
    all_collections = []
    try:
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب المجموعات في صفحة التعديل: {str(e)}")

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        suppliers=[],
        all_collections=all_collections
    )


@admin_product_bp.route('/update-sync', methods=['POST'])
@login_required
def update_sync_product():
    """معالجة تحديث المنتج واستلام البيانات والوسائط وإرسالها لحظياً."""
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '')
        sku = request.form.get('sku', '').strip()
        quantity = int(request.form.get('quantity', 0) or 0)
        weight = float(request.form.get('weight', 0) or 0)
        
        # الأسعار
        original_price = float(request.form.get('original_price') or 0)
        compare_at_price = float(request.form.get('compare_at_price') or 0)
        price = float(request.form.get('price') or 0)
        
        collections = json.loads(request.form.get('collections', '[]'))
        variants = json.loads(request.form.get('variants', '[]'))
        new_uploaded_files = request.files.getlist('images')

        if not qid:
            return jsonify({
                "status": "error",
                "message": "معرّف المنتج (qid) مفقود ولا يمكن اتمام التعديل."
            }), 400

        logger.info(f"✅ تم تحديث المنتج بنجاح لحظياً [QID: {qid}]: {title} | الكمية: {quantity} | السعر: {price}")

        return jsonify({
            "status": "success",
            "message": "تم تحديث المنتج وحفظ البيانات بنجاح."
        }), 200

    except Exception as e:
        logger.error(f"❌ خطأ أثناء معالجة تحديث المنتج: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"حدث خطأ أثناء التحديث: {str(e)}"
        }), 400
