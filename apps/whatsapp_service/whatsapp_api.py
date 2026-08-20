# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

import os
import json
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# إنشاء Blueprint لمسارات الواتساب
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

# جلب المتغيرات
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"

# ==========================================
# 1. مسار الـ Webhook
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.get_json()
    print("📩 WhatsApp Webhook Received:", json.dumps(data, indent=2))
    return jsonify({'status': 'success'}), 200

# ==========================================
# 2. دالة إرسال الرسالة النصية المباشرة (حل سريع للاختبار)
# ==========================================
def send_text_message(to_number, message_body):
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_body}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()

# ==========================================
# 3. مسار اختبار الإرسال (تم تحديثه لإرسال نص مباشر)
# ==========================================
@whatsapp_bp.route('/send-test', methods=['GET'])
def test_send_message():
    """يرسل رسالة نصية مباشرة بدلاً من قالب hello_world لتجاوز قيود ميتا"""
    target_phone = "967779077746" # رقمك الشخصي
    message_content = "مرحباً علي محجوب! تم الربط بنجاح مع سيرفر محجوب أونلاين. 🚀"
    
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        return jsonify({"status": "error", "message": "بيانات الاعتماد مفقودة"}), 400

    status, response_data = send_text_message(target_phone, message_content)
    
    return jsonify({
        "status_code": status,
        "meta_response": response_data,
        "note": "إذا فشل الإرسال، تأكد أنك أرسلت رسالة من هاتفك لرقم البوت أولاً لفتح نافذة المحادثة."
    })

# ==========================================
# 4. دالة إرسال الفاتورة (للقوالب المعتمدة)
# ==========================================
def send_invoice_whatsapp(to_number, order_id, total_price):
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
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
    response = requests.post(url, headers=headers, json=json.dumps(data))
    return response.json()
