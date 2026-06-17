# coding: utf-8
from flask import Blueprint, request, jsonify
import hmac
import hashlib
from apps.config import Config
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder
import logging

# إعداد المسار
webhooks_bp = Blueprint('webhooks', __name__)
logger = logging.getLogger(__name__)

@webhooks_bp.route('/webhooks', methods=['POST'])
def handle_qumra_webhook():
    # 1. التحقق من التوقيع الأمني (Signature Verification)
    signature = request.headers.get('X-WebHook-Signature')
    if not signature:
        return jsonify({"error": "Missing signature"}), 401

    secret = Config.WEBHOOK_SECRET.encode()
    payload = request.data
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        return jsonify({"error": "Invalid signature"}), 403

    # 2. معالجة البيانات
    data = request.get_json()
    event = data.get('event')
    order_data = data.get('data', {})

    logger.info(f"✅ تم استلام ويب هوك نوع: {event}")

    # 3. حفظ الطلب في قاعدة البيانات إذا كان حدث إنشاء طلب
    if event in ['order/created', 'cart/created']:
        order_id = str(order_data.get('id', ''))
        if order_id and not ProcessedOrder.query.get(order_id):
            new_order = ProcessedOrder(
                id=order_id,
                status=order_data.get('status', 'pending')
            )
            db.session.add(new_order)
            db.session.commit()
            logger.info(f"💾 تم حفظ الطلب {order_id} بنجاح.")

    return jsonify({"status": "success"}), 200
