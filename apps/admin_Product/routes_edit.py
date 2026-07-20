# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

import logging
from flask import render_template, flash, redirect, url_for
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

# الاستعلام الشامل لجلب تفاصيل المنتج للتعديل مع تصحيح حقول التسعير الرسمية
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
            pricing { 
                price 
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

# استعلام جلب كافة المجموعات
GET_ALL_COLLECTIONS_QUERY = """
query GetAllCollections {
    findAllCollections(input: { limit: 100 }) {
        data { qid, title }
    }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل المنتج مع كافة البيانات المحدثة والمخزون والمجموعات والموردين"""
    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        
        product_node = None
        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res:
                product_node = find_res.get('data')

        if not product_node:
            flash("❌ تعذر جلب بيانات المنتج من قمرة.", "danger")
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
                logger.error(f"⚠️ خطأ أثناء جلب بيانات الموردين: {db_err}")

        return render_template(
            'admin/admin_edit_product.html',
            product=product,
            suppliers=suppliers,
            mapping=mapping_data,
            all_collections=all_collections
        )

    except Exception as e:
        logger.error(f"❌ خطأ تقني في موديول التعديل للمنتج {qid}: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل صفحة التعديل.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))
