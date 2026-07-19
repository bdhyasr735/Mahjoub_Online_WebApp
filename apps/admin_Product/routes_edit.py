# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

# استعلام مُنظف: تم إزالة الحقول التي تسببت في خطأ الـ Validation
FIND_PRODUCT_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid
      title
      slug
      status
      views
      publishedAt
      pricing { price }
      identification { sku, barcode }
      quantity
      trackQuantity
      weight { unit }
      dimensions { length, width, height, unit }
      images { fileUrl }
      seo { title, description }
      reviewsCount
      averageRating
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
    
    try:
        # جلب المورد والبيانات الأساسية
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        suppliers = Supplier.query.filter_by(status='active').all()

        variables = {"qid": clean_qid}
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, variables)
        
        if not response or 'data' not in response:
            logger.error(f"⚠️ استجابة فارغة من قمرة لـ qid: {clean_qid}")
            flash("لا يوجد اتصال بخادم البيانات.")
            return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers)

        result = response.get('data', {}).get('findProductByQid', {})
        
        if result.get('success'):
            product = result.get('data', {})
            return render_template(
                'admin/admin_edit_product.html', 
                product=product,
                suppliers=suppliers,
                selected_supplier_id=mapping.supplier_id if mapping else None,
                internal_notes=mapping.internal_notes if mapping else ""
            )
        else:
            error_msg = result.get('message', "لم يتم العثور على المنتج في قمرة.")
            logger.warning(f"⚠️ {error_msg} لـ qid: {clean_qid}")
            flash(error_msg)
            return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers)
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب تفاصيل المنتج {clean_qid}: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل بيانات المنتج.")
        return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers)
