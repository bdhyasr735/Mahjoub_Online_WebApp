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

# استعلام جلب المنتج
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
      images { fileUrl }
      seo { title, description }
      variants
      options
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
    
    # تعريف هيكل افتراضي (فارغ) لضمان عدم حدوث خطأ UndefinedError في القالب
    mapping_data_empty = {"selected_supplier_id": None, "internal_notes": ""}
    
    try:
        # جلب الموردين المتاحين
        suppliers = Supplier.query.filter_by(status='active').all()
        
        # محاولة جلب البيانات المحلية
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {
            "selected_supplier_id": mapping.supplier_id if mapping else None,
            "internal_notes": mapping.internal_notes if mapping else ""
        }

        # جلب البيانات من قمرة
        variables = {"qid": clean_qid}
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, variables)
        
        # التحقق من استجابة قمرة
        if not response or 'data' not in response:
            logger.error(f"⚠️ استجابة فارغة من قمرة لـ qid: {clean_qid}")
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
            error_msg = result.get('message', "لم يتم العثور على المنتج.")
            flash(error_msg)
            return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers, mapping=mapping_data_empty)
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب تفاصيل المنتج {clean_qid}: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل بيانات المنتج.")
        return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers, mapping=mapping_data_empty)
