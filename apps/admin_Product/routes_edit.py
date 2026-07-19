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
    """عرض صفحة تعديل المنتج باستخدام الهيكلية المحدثة"""
    
    # الاستعلام المحدث ليتوافق مع وجود كائن 'data' في الرد
    product_query = """
    query GetProductDetail($qid: String!) { 
        findProductByQid(qid: $qid) { 
            data {
                qid
                title
                slug
                description
                pricing {
                    price
                    currency
                }
                identification {
                    sku
                    barcode
                }
                quantity
                collections {
                    qid
                }
            }
        } 
    }
    """
    
    collections_query = """
    query GetAllCollections {
        findAllCollections(input: { limit: 100 }) {
            data {
                qid
                title
            }
        }
    }
    """

    try:
        # تنفيذ الاستعلام مع تمرير qid كـ String
        prod_response = QomrahGraphQLClient.execute_query(product_query, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(collections_query)
        
        # التأكد من المسار الصحيح في الاستجابة (findProductByQid -> data)
        if not prod_response or 'data' not in prod_response or not prod_response['data'].get('findProductByQid', {}).get('data'):
            flash("❌ تعذر جلب بيانات المنتج من منصة قمرة.")
            return redirect(url_for('admin_product_bp.manage_products'))
            
        # الوصول المباشر للبيانات المطلوبة داخل كائن 'data'
        product = prod_response['data']['findProductByQid']['data']
        
        # تحويل المجموعات لتناسب القالب
        product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c]
        
        all_collections = []
        if col_response and 'data' in col_response and col_response['data'].get('findAllCollections'):
            all_collections = col_response['data']['findAllCollections'].get('data', [])

        suppliers = []
        mapping_data = {"selected_supplier_id": None}
        
        if HAS_MODELS:
            try:
                suppliers = Supplier.query.all()
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if mapping:
                    mapping_data["selected_supplier_id"] = mapping.supplier_id
            except Exception as db_err:
                logger.error(f"⚠️ خطأ أثناء جلب الموردين: {db_err}")

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
