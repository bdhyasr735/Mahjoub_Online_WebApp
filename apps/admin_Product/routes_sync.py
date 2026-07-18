# coding: utf-8
# 📂 apps/admin_Product/routes_sync.py

from flask import request, jsonify
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """
    مسار لحفظ بيانات منتج محدد وإرسال التحديثات إلى منصة قمرة
    """
    data = request.get_json()
    if not data or 'qid' not in data:
        return jsonify({"status": "error", "message": "بيانات غير صالحة"}), 400

    try:
        # بناءً على هيكل قمرة، التحديث يتم عبر Mutation مخصص للمعلومات
        # مثال: تحديث العنوان والوصف والكمية
        mutation = """
        mutation UpdateProductInfo($id: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(id: $id, input: $input) {
                qid
                title
            }
        }
        """
        
        # تجهيز المدخلات حسب الـ Schema المتوقعة
        variables = {
            "id": data['qid'],
            "input": {
                "title": data.get('title'),
                "quantity": int(data.get('quantity', 0))
                # أضف بقية الحقول المتاحة في UpdateProductInfoInput
            }
        }
        
        response = QomrahGraphQLClient.execute_query(mutation, variables=variables)
        
        # التحقق من استجابة الـ GraphQL
        if not response or 'errors' in response:
            logger.error(f"❌ خطأ من قمرة: {response.get('errors')}")
            return jsonify({"status": "error", "message": "فشلت عملية التحديث في قمرة"}), 400
        
        logger.info(f"✅ تم تحديث المنتج بنجاح: {data.get('qid')}")
        return jsonify({
            "status": "success", 
            "message": "تم تحديث البيانات بنجاح"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ خطأ داخلي أثناء الحفظ: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع"}), 500
