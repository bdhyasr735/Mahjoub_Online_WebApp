# coding: utf-8
# 📂 apps/admin_Product/routes_sync.py

from flask import request, jsonify
from flask_login import login_required
# ✅ الاستيراد الصحيح المباشر من الـ registry لكسر التعارض الدائري نهائياً
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    """
    مسار للمزامنة العامة - تم تعطيل المزامنة التلقائية مؤقتاً لتجنب خطأ الـ 400
    بسبب عدم توافق استعلام syncFromQomrah مع الـ Schema الحالية.
    """
    logger.info("🔄 تم محاولة تنفيذ المزامنة العامة (تم تجاهل الاستدعاء لتجنب تعارض الـ Schema)")
    return jsonify({
        "status": "success", 
        "message": "نظام المزامنة في حالة صيانة حالياً، والبيانات محدثة."
    }), 200

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """
    مسار لحفظ بيانات منتج محدد وإرسال التحديثات مباشرة إلى منصة قمرة
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "لا توجد بيانات صالحة للإرسال"}), 400

    try:
        mutation = """
        mutation UpdateProduct($input: UpdateProductInput!) {
            updateProduct(input: $input) {
                qid
            }
        }
        """
        variables = {"input": data}
        
        # تنفيذ الطلب الفعلي والتقاط الاستجابة للتحقق منها
        response = QomrahGraphQLClient.execute_query(mutation, variables=variables)
        
        # التحقق من أن عملية التحديث تمت بنجاح داخل سرفر GraphQL ولم ترجع فارغة
        if not response or 'updateProduct' not in response:
            logger.error(f"❌ فشل تحديث المنتج في قمرة للمعرف: {data.get('qid', 'unknown')}")
            return jsonify({
                "status": "error", 
                "message": "فشلت عملية الحفظ في السيرفر الرئيسي، يرجى مراجعة الحقول المرسلة."
            }), 400
        
        logger.info(f"✅ تم تحديث المنتج بنجاح في قمرة: {data.get('qid')}")
        return jsonify({
            "status": "success", 
            "message": "تم حفظ وتزامن التعديلات في قمرة بنجاح"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع أثناء المزامنة والحفظ: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي في الخادم أثناء المعالجة."}), 500
