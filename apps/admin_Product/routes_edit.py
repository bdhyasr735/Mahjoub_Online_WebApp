# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, request, jsonify
from flask_login import login_required
from .registry import admin_product_bp 
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models.suppliers_db import Supplier # استيراد الموردين للربط
import logging

logger = logging.getLogger(__name__)

# 🚀 تم تحديث اسم الحقل ليتوافق مع API قمرة (findProductByQid)
FIND_PRODUCT_QUERY = """
query GetProduct($qid: ID!) {
  findProductByQid(qid: $qid) {
    qid
    title
    quantity
    pricing { price }
    images { fileUrl }
  }
}
"""

@admin_product_bp.route('/edit/<qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """
    راوتر لجلب بيانات المنتج وعرض صفحة التعديل مع قائمة الموردين.
    """
    try:
        # 1. جلب البيانات من قمرة
        result = QomrahGraphQLClient.execute_query(FIND_PRODUCT_QUERY, variables={"qid": qid})
        
        # 2. التحقق من وجود البيانات لمنع الانهيار (Crash)
        if not result or 'data' not in result or not result['data'].get('findProductByQid'):
            logger.error(f"❌ المنتج غير موجود أو خطأ في الاستعلام لـ {qid}: {result}")
            return "المنتج غير موجود في قاعدة بيانات قمرة", 404
            
        product = result['data']['findProductByQid']
        
        # 3. جلب قائمة الموردين من قاعدة بياناتنا المحلية للربط
        suppliers = Supplier.query.all()
        
        # 4. عرض الصفحة مع بيانات المنتج وقائمة الموردين
        return render_template('admin/admin_edit_product.html', 
                               product=product, 
                               suppliers=suppliers)
        
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج {qid}: {e}")
        return "حدث خطأ أثناء معالجة بيانات المنتج", 500

@admin_product_bp.route('/update-product', methods=['POST'])
@login_required
def update_product():
    """
    راوتر لاستقبال تحديثات المنتج (عبر AJAX).
    """
    data = request.get_json()
    if not data or 'qid' not in data:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
        
    mutation = """
    mutation UpdateProduct($input: UpdateProductInput!) {
      updateProduct(input: $input) {
        status
        message
      }
    }
    """
    
    try:
        result = QomrahGraphQLClient.execute_query(mutation, variables={"input": data}) or {}
        response_data = result.get('data', {}).get('updateProduct', {})
        
        if response_data.get('status') == 'success':
            logger.info(f"✅ تم تحديث المنتج {data['qid']} بنجاح")
            return jsonify({"status": "success", "message": "تم التحديث بنجاح"})
        else:
            return jsonify({"status": "error", "message": response_data.get('message', 'فشل التحديث')})
        
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تحديث المنتج {data.get('qid')}: {e}")
        return jsonify({"status": "error", "message": "فشل الاتصال بنظام التحديث"}), 500
