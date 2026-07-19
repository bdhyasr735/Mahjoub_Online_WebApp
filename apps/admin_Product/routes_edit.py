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

# استعلام جلب تفاصيل المنتج بالكامل وفق الهيكل المطلوب
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
      pricing { price, compareAtPrice, costPrice, currency }
      identification { sku, barcode }
      quantity
      trackQuantity
      weight { value, unit }
      dimensions { length, width, height, unit }
      images { fileUrl }
      collections { name }
      seo { title, description }
      options { name, values }
      reviewsCount
      averageRating
    }
  }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """جلب بيانات المنتج من قمرة وعرضها في صفحة التعديل مع ربط المورد"""
    
    if not qid:
        flash("معرف المنتج مفقود.")
        return redirect(url_for('admin_product_bp.manage_products'))

    # فك الترميز المزدوج للـ qid
    clean_qid = unquote(unquote(qid))
    
    try:
        # 1. جلب المورد المرتبط بهذا المنتج من قاعدة بياناتنا
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        
        # 2. جلب جميع الموردين النشطين للقائمة المنسدلة في الواجهة
        suppliers = Supplier.query.filter_by(status='active').all()

        # 3. إرسال الاستعلام الشامل لقمرة لجلب بيانات المنتج
        variables = {"qid": clean_qid}
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, variables)
        
        if not response:
            logger.error(f"⚠️ استجابة فارغة من قمرة لـ qid: {clean_qid}")
            flash("لا يوجد اتصال بخادم البيانات.")
            return render_template('admin/admin_edit_product.html', product={}, suppliers=suppliers)

        data_payload = response.get('data', {})
        result = data_payload.get('findProductByQid', {})
        
        if result.get('success'):
            product = result.get('data', {})
            # إرسال البيانات كاملة للـ Template
            return render_template(
                'admin/admin_edit_product.html', 
                product=product,
                suppliers=suppliers,
                selected_supplier_id=mapping.supplier_id if mapping else None
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
