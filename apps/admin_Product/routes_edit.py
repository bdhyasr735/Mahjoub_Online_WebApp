# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

FIND_PRODUCT_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid, title, description, slug, status, quantity, trackQuantity
      pricing { price, compareAtPrice, originalPrice }
      images { fileUrl }
      variants { title, pricing { price }, quantity, identification { sku } }
      collections { qid, title }
    }
  }
}
"""

LIST_COLLECTIONS_QUERY = """
query {
  findAllCollections {
    data { qid, title }
  }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    clean_qid = unquote(unquote(qid))
    try:
        # جلب الموردين والمجموعات بشكل منفصل لتجنب انهيار الصفحة
        suppliers = Supplier.query.filter_by(status='active').all()
        
        col_res = QomrahGraphQLClient.execute_query(LIST_COLLECTIONS_QUERY)
        all_collections = []
        if col_res and 'data' in col_res:
            all_collections = col_res['data'].get('findAllCollections', {}).get('data', [])

        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {"selected_supplier_id": mapping.supplier_id if mapping else None}

        # جلب المنتج
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, {"qid": clean_qid})
        
        product_data = {}
        if response and 'data' in response and response['data'].get('findProductByQid', {}).get('success'):
            product_data = response['data']['findProductByQid'].get('data', {})
            # معالجة المتغيرات (Flattening)
            for v in product_data.get('variants', []):
                v['price'] = v.get('pricing', {}).get('price', 0) if v.get('pricing') else 0
                v['sku'] = v.get('identification', {}).get('sku', '') if v.get('identification') else ''
            
            product_data['collection_qids'] = [c['qid'] for c in product_data.get('collections', [])] if product_data.get('collections') else []

        return render_template(
            'admin/admin_edit_product.html', 
            product=product_data, 
            suppliers=suppliers, 
            all_collections=all_collections, 
            mapping=mapping_data
        )
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح في edit_product: {str(e)}")
        # نرجع صفحة فارغة بدلاً من تعطل التطبيق
        return render_template('admin/admin_edit_product.html', product={}, suppliers=[], all_collections=[], mapping={})
