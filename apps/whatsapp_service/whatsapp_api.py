import os
import json
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# إنشاء Blueprint لمسارات الواتساب
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

# جلب المتغيرات (مع دعم الأسماء المعتمدة في Render)
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")
VERSION = os.getenv("VERSION", "v18.0")
BASE_URL = os.getenv("BASE_URL", "https://graph.facebook.com")

# ==========================================
# 1. مسار الـ Webhook (استقبال والتحقق من Meta)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """التحقق من الرابط عند ربطه في لوحة Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return jsonify({'status': 'error', 'message': 'Verification failed'}), 403
    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    """استقبال الرسائل والتحديثات الواردة من المستخدمين"""
    data = request.get_json()
    print("📩 WhatsApp Webhook Received:", json.dumps(data, indent=2))
    return jsonify({'status': 'success'}), 200

# ==========================================
# 2. دالة إرسال الفاتورة (إرسال صادر)
# ==========================================
def send_invoice_whatsapp(to_number, order_id, total_price):
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        print("❌ خطأ: لم يتم العثور على بيانات الاعتماد")
        return {"error": "Missing credentials"}

    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "order_invoice", 
            "language": {"code": "ar"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(order_id)},
                    {"type": "text", "text": str(total_price)}
                ]
            }]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()
    except Exception as e:
        return {"error": str(e)}
