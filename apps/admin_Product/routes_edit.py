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

# استعلام جلب المنتج المحدث ليشمل حقل description
FIND_PRODUCT_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid
      title
      description
      slug
      status
      quantity
      trackQuantity
      pricing {
        price
        compareAtPrice
        originalPrice
      }
      identification {
        sku
        barcode
      }
      images { fileUrl }
      seo {
        title
        description
      }
      averageRating
      reviewsCount
    }
  }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    if not qid:
        flash("معرف المنتج مفقود.")
        return redirect(url_for('admin_product_bp.manage_products'))

    clean_qid = unquote(unquote(qid))
    
    mapping_data_empty = {"selected_supplier_id": None, "internal_notes": ""}
    
    try:
        # 1. جلب الموردين المتاحين
        suppliers = Supplier.query.filter_by(status='active').all()
        
        # 2. استحضار البيانات المحلية للمنتج
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {
            "selected_supplier_id": mapping.supplier_id if mapping else None,
            "internal_notes": mapping.internal_notes if mapping else ""
        }

        # 3. استحضار البيانات من قمرة
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, {"qid": clean_qid})
        
        if not response or 'data' not in response:
            logger.error(f"⚠️ فشل الاتصال بقمرة لـ qid: {clean_qid}")
            flash("لا يوجد اتصال بخادم البيانات.")
            return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers, mapping=mapping_data_empty)

        result = response.get('data', {}).get('findProductByQid', {})
        
        if result.get('success'):
            return render_template(
                'admin/admin_edit_product.html', 
                product=result.get('data', {}),
                suppliers=suppliers,
                mapping=mapping_data
            )
        else:
            flash(result.get('message', "لم يتم العثور على المنتج."))
            return redirect(url_for('admin_product_bp.manage_products'))
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء استحضار المنتج {clean_qid}: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل بيانات المنتج.")
        return redirect(url_for('admin_product_bp.manage_products'))
