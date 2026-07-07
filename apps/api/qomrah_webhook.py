# coding: utf-8
# 📂 apps/api/qomrah_webhook.py

import hashlib
import hmac
import logging
from flask import Blueprint, request, jsonify
from apps.api.sync_engine import SyncEngine
from apps.services.graphql_client import QomrahGraphQLClient
from config import Config

logger = logging.getLogger(__name__)

# تعريف الـ Blueprint ليتم تسجيله في __init__.py
qomrah_bp = Blueprint('qomrah_webhook', __name__)

def verify_signature(payload, signature):
    """التحقق من أن الطلب قادم فعلاً من قمرة عبر HMAC."""
    if not signature: return False
    expected_signature = hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@qomrah_bp.route('/api/qomrah/webhook', methods=['POST'])
def handle_qomrah_webhook():
    signature = request.headers.get('X-Qomrah-Signature')
    payload = request.data

    # 1. التحقق الأمني
    if not verify_signature(payload, signature):
        logger.warning("❌ محاولة دخول غير مصرح بها للـ Webhook")
        return jsonify({"status": "error", "message": "Invalid signature"}), 403

    data = request.json
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({"status": "error", "message": "Missing order_id"}), 400

    try:
        # 2. جلب البيانات الكاملة من قمرة عبر GraphQL
        full_order_data = QomrahGraphQLClient.get_order_details(order_id)
        
        if not full_order_data:
            return jsonify({"status": "error", "message": "Order not found in Qumra"}), 404

        # 3. تمرير البيانات لمحرك المزامنة (SyncEngine)
        success = SyncEngine.process_financials(full_order_data)
        
        if success:
            return jsonify({"status": "success", "order_id": order_id}), 200
        else:
            return jsonify({"status": "error", "message": "Sync failed"}), 500

    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الـ Webhook للطلب {order_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
