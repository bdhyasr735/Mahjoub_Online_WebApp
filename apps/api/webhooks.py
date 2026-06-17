# coding: utf-8
# 📂 apps/api/webhooks.py - معالج الويب هوك الاحترافي

from flask import Blueprint, request, jsonify
import logging
import hmac
import hashlib
from apps import Config

# إعداد السجلات (Logs) لمراقبة الطلبات في Render
logger = logging.getLogger(__name__)

# إنشاء Blueprint للويب هوك
webhooks_bp = Blueprint('webhooks', __name__)

def verify_signature(data, signature):
    """التحقق من أن الطلب قادم فعلاً من منصة قمرا باستخدام HMAC-SHA256"""
    # نستخدم المفتاح السري المخزن في Config (الذي قمت بضبطه في متغيرات البيئة على Render)
    secret = Config.WEBHOOK_SECRET
    
    if not secret:
        logger.warning("⚠️ تحذير: WEBHOOK_SECRET غير مضبوط في الإعدادات!")
        return True # في حال التطوير يمكنك السماح بالمرور
    
    # حساب التوقيع المتوقع
    expected_signature = hmac.new(
        secret.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    
    # مقارنة التوقيع بأمان
    return hmac.compare_digest(expected_signature, signature)

@webhooks_bp.route('/api/webhooks/qumra', methods=['POST'])
def handle_qumra_webhook():
    # 1. التحقق من وجود التوقيع في Headers
    signature = request.headers.get('X-WebHook-Signature')
    
    # 2. التحقق الأمني
    if not signature or not verify_signature(request.data, signature):
        logger.error("❌ محاولة دخول غير مصرح بها: توقيع غير متطابق!")
        return jsonify({"error": "Invalid signature"}), 403

    # 3. استقبال البيانات
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    # 4. تسجيل الحدث للتشخيص
    event_type = data.get('event', 'unknown')
    logger.info(f"✅ تم استلام حدث بنجاح: {event_type} | ID: {data.get('data', {}).get('_id')}")
    
    # 5. هنا يمكنك إضافة منطق العمل (مثل استدعاء SyncEngine)
    # مثال:
    # if event_type == 'order/created':
    #     sync_order(data['data'])
    
    # 6. الرد على المنصة بأن العملية تمت بنجاح
    return jsonify({"status": "success", "message": "Event processed"}), 200
