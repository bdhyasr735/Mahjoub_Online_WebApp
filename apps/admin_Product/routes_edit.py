# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

try:
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.models.supplier import Supplier
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False

logger = logging.getLogger(__name__)

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل المنتج مع كافة البيانات المحدثة والمخزون والشحن"""
    
    # 1. الاستعلام لجلب تفاصيل المنتج الشاملة
    product_query = """
    query GetProductDetail($qid: String!) { 
        findProductByQid(qid: $qid) { 
            data {
                qid
                title
                slug
                description
                status
                sku
                quantity
                weight
                pricing { price, compareAtPrice, originalPrice }
                images { fileUrl }
                collections { qid, title }
                variants { quantity, sku, pricing { price } }
            }
        } 
    }
    """
    
    # 2. الاستعلام لجلب كافة المجموعات
    collections_query = """
    query GetAllCollections {
        findAllCollections(input: { limit: 100 }) {
            data { qid, title }
        }
    }
    """

    try:
        prod_response = QomrahGraphQLClient.execute_query(product_query, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(collections_query)
        
        if not prod_response or not prod_response.get('data', {}).get('findProductByQid', {}).get('data'):
            flash("❌ تعذر جلب بيانات المنتج.")
            return redirect(url_for('admin_product_bp.manage_products'))
            
        product = prod_response['data']['findProductByQid']['data']
        
        # تجهيز البيانات للقالب
        product['images'] = [img['fileUrl'] for img in product.get('images', []) if img.get('fileUrl')]
        product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c and c.get('qid')]
        
        # جلب كافة المجموعات
        all_collections = []
        if col_response and 'data' in col_response and col_response['data'].get('findAllCollections'):
            all_collections = col_response['data']['findAllCollections'].get('data', [])

        # جلب الموردين وربطهم
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
        logger.error(f"❌ خطأ تقني في موديول التعديل: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل الصفحة.")
        return redirect(url_for('admin_product_bp.manage_products'))
