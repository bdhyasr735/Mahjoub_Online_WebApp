# 📂 apps/api/webhooks.py
from flask import Blueprint, request, jsonify
import hmac
import hashlib
from apps.config import Config

# إنشاء Blueprint جديد
webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/api/webhooks/qumra', methods=['POST'])
def handle_qumra_webhook():
    # 1. التحقق الأمني باستخدام التوقيع
    signature = request.headers.get('X-WebHook-Signature')
    secret = Config.WEBHOOK_SECRET.encode()
    
    # حساب التوقيع للمقارنة
    expected_signature = hmac.new(secret, request.data, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        return jsonify({"error": "Invalid signature"}), 403

    # 2. استقبال بيانات الويب هوك الخام
    data = request.get_json()
    
    # 3. إرسال البيانات للمعالجة (بدون المرور عبر GraphQL)
    print(f"✅ تم استقبال ويب هوك بنجاح: {data.get('event')}")
    
    # هنا سيتم لاحقاً استدعاء محرك المزامنة (SyncEngine) لحفظ الطلب
    return jsonify({"status": "success"}), 200
