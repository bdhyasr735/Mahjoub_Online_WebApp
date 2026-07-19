# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from apps import db
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

# استعلام تحديث بيانات المنتج
UPDATE_PRODUCT_MUTATION = """
mutation UpdateProduct($qid: String!, $data: ProductUpdateInput!) {
  updateProduct(qid: $qid, data: $data) {
    success
    message
  }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    # فك الترميز للتأكد من وصول المعرف بشكل صحيح
    clean_qid = unquote(qid)
    
    try:
        # جلب الموردين النشطين
        suppliers = Supplier.query.filter_by(status='active').all()
        
        # جلب المجموعات
        col_response = QomrahGraphQLClient.execute_query("""query { listCollections { data { qid, title } } }""")
        all_collections = col_response.get('data', {}).get('listCollections', {}).get('data', []) if col_response else []
        
        # جلب بيانات المورد المحلي
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {"selected_supplier_id": mapping.supplier_id if mapping else None}

        # جلب بيانات المنتج من قمرة
        prod_query = """query GetProd($qid: String!) { findProductByQid(qid: $qid) { success data { qid, title, description, slug, variants { title, price, quantity, sku }, collections { qid } } } }"""
        response = QomrahGraphQLClient.execute_query(prod_query, {"qid": clean_qid})
        
        product_data = response.get('data', {}).get('findProductByQid', {}).get('data', {})
        
        if not product_data:
            flash("المنتج غير موجود أو لا يمكن الوصول إليه.")
            return redirect(url_for('admin_product_bp.manage_products'))

        product_data['collection_ids'] = [c['qid'] for c in product_data.get('collections', [])]

        return render_template('admin/admin_edit_product.html', 
                               product=product_data, 
                               suppliers=suppliers, 
                               all_collections=all_collections, 
                               mapping=mapping_data)
    except Exception as e:
        logger.error(f"خطأ في تحميل صفحة التعديل: {str(e)}")
        flash("حدث خطأ أثناء تحميل بيانات المنتج.")
        return redirect(url_for('admin_product_bp.manage_products'))

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    data = request.json
    qid = data.get('qid')
    
    if not qid:
        return jsonify({"status": "error", "message": "معرف المنتج مفقود"}), 400
    
    try:
        # 1. تحديث قاعدة البيانات المحلية (المورد)
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
        if not mapping:
            mapping = ProductSupplierMapping(product_qid=qid)
            db.session.add(mapping)
        mapping.supplier_id = data.get('supplier_id')
        db.session.commit()

        # 2. إرسال التحديث إلى قمرة
        mutation_data = {
            "title": data.get('title'),
            "description": data.get('description'),
            "variants": data.get('variants'),
            "collectionIds": data.get('collection_ids')
        }
        
        response = QomrahGraphQLClient.execute_query(UPDATE_PRODUCT_MUTATION, {"qid": qid, "data": mutation_data})
        
        if response and response.get('data', {}).get('updateProduct', {}).get('success'):
            return jsonify({"status": "success", "message": "تم حفظ البيانات بنجاح"})
        else:
            return jsonify({"status": "error", "message": "فشل الحفظ في خادم قمرة"}), 400
            
    except Exception as e:
        logger.error(f"خطأ أثناء الحفظ: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع أثناء الحفظ"}), 500
