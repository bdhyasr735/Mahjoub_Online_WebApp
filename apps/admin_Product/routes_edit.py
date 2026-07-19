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

# تم تعديل الاستعلام ليتوافق مع أخطاء الـ Validation في السجلات
FIND_PRODUCT_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid, title, description, slug, status, quantity, trackQuantity
      pricing { price, compareAtPrice, originalPrice }
      images { fileUrl }
      variants { qid, title, pricing { price }, quantity, identification { sku } }
      collections { qid, title }
    }
  }
}
"""

# تم التصحيح إلى findAllCollections بناءً على رسالة الخطأ
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
    if not qid: return redirect(url_for('admin_product_bp.manage_products'))
    clean_qid = unquote(unquote(qid))
    
    try:
        suppliers = Supplier.query.filter_by(status='active').all()
        
        # جلب المجموعات بالاستعلام المصحح
        col_response = QomrahGraphQLClient.execute_query(LIST_COLLECTIONS_QUERY)
        all_collections = col_response.get('data', {}).get('findAllCollections', {}).get('data', []) if col_response else []
        
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {"selected_supplier_id": mapping.supplier_id if mapping else None}

        # جلب المنتج
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, {"qid": clean_qid})
        result = response.get('data', {}).get('findProductByQid', {})
        
        if result.get('success'):
            product_data = result.get('data', {})
            # معالجة المتغيرات لتناسب القالب (Flattening)
            for v in product_data.get('variants', []):
                v['price'] = v.get('pricing', {}).get('price', 0)
                v['sku'] = v.get('identification', {}).get('sku', '')
            
            product_data['collection_qids'] = [col['qid'] for col in product_data.get('collections', [])]
            return render_template('admin/admin_edit_product.html', product=product_data, suppliers=suppliers, all_collections=all_collections, mapping=mapping_data)
        
        flash("فشل جلب البيانات.")
        return redirect(url_for('admin_product_bp.manage_products'))
            
    except Exception as e:
        logger.error(f"❌ خطأ: {str(e)}")
        return redirect(url_for('admin_product_bp.manage_products'))
