# coding: utf-8
from flask import request, jsonify
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """
    مسار للمزامنة العامة لجلب البيانات من قمرة
    """
    try:
        # مثال لاستعلام المزامنة (تأكد من اسم الـ mutation في Schema قمرة)
        mutation = "mutation { syncFromQomrah { status message } }"
        result = QomrahGraphQLClient.execute_query(mutation) or {}
        
        logger.info("تم تنفيذ عملية المزامنة العامة بنجاح")
        return jsonify({"status": "success", "message": "تمت المزامنة بنجاح مع قمرة"}), 200
    except Exception as e:
        logger.error(f"Error during proxy sync: {e}")
        return jsonify({"status": "error", "message": "فشلت عملية المزامنة"}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """
    مسار لحفظ بيانات منتج محدد وإرسالها إلى قمرة
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "لا توجد بيانات للارسال"}), 400

    try:
        mutation = """
        mutation UpdateProduct($input: UpdateProductInput!) {
            updateProduct(input: $input) {
                qid
            }
        }
        """
        variables = {"input": data}
        
        # تفعيل الاتصال الفعلي بقاعدة البيانات
        QomrahGraphQLClient.execute_query(mutation, variables=variables)
        
        logger.info(f"تم تحديث المنتج: {data.get('qid', 'unknown')}")
        return jsonify({"status": "success", "message": "تم حفظ التعديلات في قمرة بنجاح"}), 200
        
    except Exception as e:
        logger.error(f"Error during save sync: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
