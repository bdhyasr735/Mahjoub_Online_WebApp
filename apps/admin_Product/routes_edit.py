# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

# استعلام جلب تفاصيل منتج واحد بناءً على هيكل Schema قمرة الصحيح
FIND_PRODUCT_QUERY = """
query GetProduct($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid
      title
      pricing { price }
      quantity
      images { fileUrl }
      identification { sku }
    }
  }
}
"""

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """جلب بيانات المنتج من قمرة وعرضها في صفحة التعديل"""
    
    # التأكد من وجود qid
    if not qid:
        flash("معرف المنتج مفقود.")
        return redirect(url_for('admin_product_bp.manage_products'))

    # فك ترميز الـ qid (مستوى مزدوج للتعامل مع الروابط المشفرة)
    clean_qid = unquote(unquote(qid))
    
    try:
        # إرسال الاستعلام للمصدر
        variables = {"qid": clean_qid}
        response = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, variables)
        
        # التأكد من صحة استجابة GraphQL
        if not response:
            logger.error(f"⚠️ استجابة فارغة من قمرة لـ qid: {clean_qid}")
            flash("لا يوجد اتصال بخادم البيانات.")
            return render_template('admin/admin_edit_product.html', product={})

        # استخراج البيانات
        data_payload = response.get('data', {})
        result = data_payload.get('findProductByQid', {})
        
        if result.get('success'):
            product = result.get('data', {})
            return render_template('admin/admin_edit_product.html', product=product)
        else:
            error_msg = result.get('message', "لم يتم العثور على المنتج في قمرة.")
            logger.warning(f"⚠️ {error_msg} لـ qid: {clean_qid}")
            flash(error_msg)
            return render_template('admin/admin_edit_product.html', product={})
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب تفاصيل المنتج {clean_qid}: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل بيانات المنتج.")
        return render_template('admin/admin_edit_product.html', product={})
