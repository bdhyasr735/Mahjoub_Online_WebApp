# coding: utf-8
# 📂 apps/api/webhooks.py - معالج الويب هوك المطور للعمل مع SyncEngine

import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify
from config import Config 
from apps.api.sync_engine import SyncEngine

# إعداد السجلات
logger = logging.getLogger(__name__)
webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/webhooks', methods=['POST'])
def handle_qumra_webhook():
    """
    معالج الويب هوك: التحقق من التوقيع ثم تمرير البيانات لمحرك المزامنة.
    """
    
    # 1. التحقق من التوقيع (الأمن أولاً)
    signature = request.headers.get('X-WebHook-Signature') or request.headers.get('X-Signature')
    if not signature:
        logger.warning("⚠️ محاولة اتصال بدون توقيع")
        return jsonify({"error": "Missing signature"}), 401

    secret = Config.WEBHOOK_SECRET.strip().encode('utf-8')
    payload = request.get_data()
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.error(f"🚫 توقيع غير صالح. متوقع: {expected_signature}, مستلم: {signature}")
        return jsonify({"error": "Invalid signature"}), 403

    # 2. استخراج البيانات
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    event = data.get('event')
    # في حال كان الـ Webhook يرسل البيانات داخل 'data' أو بشكل مباشر
    order_data = data.get('data', data) 
    
    logger.info(f"✅ استلام حدث: {event} | معالجة الطلب: {order_data.get('id')}")

    # 3. تمرير المعالجة للمحرك السيادي (SyncEngine)
    # هذا يغنينا عن كتابة كود الحفظ والمالية هنا، ويجعل المحرك هو المسؤول الوحيد
    if event in ['order/created', 'order/updated', 'cart/created']:
        try:
            success = SyncEngine.process_financials(order_data)
            
            if success:
                logger.info(f"💾 تم معالجة الطلب {order_data.get('id')} بنجاح عبر SyncEngine.")
                return jsonify({"status": "success"}), 200
            else:
                logger.error(f"❌ فشل معالجة الطلب {order_data.get('id')} في المحرك.")
                return jsonify({"error": "Processing failed"}), 500
                
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع أثناء معالجة الويب هوك: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    return jsonify({"status": "ignored", "message": "Event not handled"}), 200
