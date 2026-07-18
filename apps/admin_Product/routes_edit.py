# apps/admin_Product/routes_edit.py

# coding: utf-8
from flask import render_template, request, jsonify
from flask_login import login_required
from .routes import admin_product_bp 
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/edit/<qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """
    راوتر لجلب بيانات المنتج وعرض صفحة التعديل.
    """
    query = """
    query GetProduct($qid: String!) {
      findProductByQid(qid: $qid) {
        qid
        title
        quantity
        pricing {
          price
        }
        identification {
          sku
        }
        images {
          fileUrl
        }
      }
    }
    """
    
    try:
        # تنفيذ الاستعلام لجلب بيانات المنتج الحالي من "قمرة"
        result = QomrahGraphQLClient.execute_query(query, variables={"qid": qid}) or {}
        product = result.get('findProductByQid')
        
        if not product:
            logger.error(f"Product not found: {qid}")
            return "المنتج غير موجود", 404
            
        return render_template('admin/admin_edit_product.html', product=product)
        
    except Exception as e:
        logger.error(f"Error fetching product {qid}: {e}")
        return "حدث خطأ أثناء جلب بيانات المنتج", 500

@admin_product_bp.route('/update-product', methods=['POST'])
@login_required
def update_product():
    """
    راوتر لاستقبال تحديثات المنتج (يتم استدعاؤه عبر AJAX من صفحة التعديل).
    """
    data = request.get_json()
    if not data or 'qid' not in data:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
        
    try:
        # ملاحظة: قم بتعريف الـ Mutation الخاص بك هنا وفقاً لمتطلبات "قمرة"
        # mutation = "mutation UpdateProduct($input: UpdateProductInput!) { ... }"
        # QomrahGraphQLClient.execute_query(mutation, variables={"input": data})
        
        logger.info(f"Updating product {data['qid']} with data: {data}")
        return jsonify({"status": "success", "message": "تم تحديث المنتج بنجاح"})
        
    except Exception as e:
        logger.error(f"Error updating product {data.get('qid')}: {e}")
        return jsonify({"status": "error", "message": "فشل التحديث في النظام"}), 500
