# coding: utf-8
# 📂 apps/admin_Product/routes_sync.py

from flask import request, jsonify
from flask_login import login_required
# ✅ الاستيراد الصحيح المباشر من الـ registry لضمان الإقلاع المستقل والآمن
from .registry import admin_product_bp 
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    logger.info("🔄 طلب مزامنة عامة")
    return jsonify({"status": "success", "message": "البيانات محدثة."}), 200

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "لا توجد بيانات صالحة"}), 400

    try:
        mutation = """
        mutation UpdateProduct($input: UpdateProductInput!) {
            updateProduct(input: $input) { qid }
        }
        """
        response = QomrahGraphQLClient.execute_query(mutation, variables={"input": data})
        if not response or 'updateProduct' not in response:
            return jsonify({"status": "error", "message": "فشلت عملية الحفظ في السيرفر الرئيسي"}), 400
        
        return jsonify({"status": "success", "message": "تم حفظ التعديلات بنجاح"}), 200
    except Exception as e:
        logger.error(f"❌ خطأ أثناء المزامنة: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي في الخادم."}), 500
