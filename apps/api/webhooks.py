# coding: utf-8
from flask import Blueprint, request, jsonify
import hmac
import hashlib
import logging
from apps import Config

# إعداد السجلات لمراقبة الطلبات في Render Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء Blueprint خاص بالويب هوك
webhooks_bp = Blueprint('webhooks', __name__)

# استخدام مفتاح التوقيع من الإعدادات
WEBHOOK_SECRET = Config.WEBHOOK_SECRET

def verify_signature(data, signature):
    """التحقق من أن الطلب قادم فعلاً من منصة قمرا"""
    if not WEBHOOK_SECRET:
        return True # للسماح بالمرور في حال عدم وجود مفتاح
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@webhooks_bp.route('/api/webhooks/qumra', methods=['POST'])
def handle_qumra_webhook():
    # 1. التحقق من التوقيع الأمني القادم في الـ Headers
    signature = request.headers.get('X-WebHook-Signature')
    
    if not signature or not verify_signature(request.data, signature):
        logger.error("❌ محاولة اختراق أو توقيع غير صالح!")
        return jsonify({"error": "Invalid signature"}), 403

    # 2. استقبال البيانات
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    # 3. تسجيل الحدث للتشخيص
    event_type = data.get('event', 'unknown')
    logger.info(f"✅ تم استلام حدث بنجاح: {event_type}")
    
    # 4. معالجة الأحداث بناءً على نوعها
    # يمكنك توسيع هذا الجزء لإضافة منطق العمل الخاص بك
    try:
        if event_type == 'cart/created':
            # مثال: التعامل مع إنشاء سلة جديدة
            logger.info(f"🛒 معالجة سلة جديدة: {data.get('data', {}).get('_id')}")
        elif event_type == 'order/created':
            # مثال: التعامل مع طلب جديد
            logger.info("📦 تم استلام طلب جديد")
            
        # إرجاع رد للمنصة بأن العملية تمت بنجاح
        return jsonify({"status": "success", "message": "Event processed"}), 200
        
    except Exception as e:
        logger.error(f"⚠️ خطأ أثناء المعالجة: {str(e)}")
        return jsonify({"status": "error", "message": "Processing failed"}), 500
