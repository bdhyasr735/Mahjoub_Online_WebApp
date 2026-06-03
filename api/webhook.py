import requests
from flask import Blueprint, request, jsonify

# إنشاء Blueprint لتنظيم الـ API
webhook_bp = Blueprint('webhook_bp', __name__)

# الإعدادات
VERIFY_TOKEN = "Mahjoob_WhatsApp_Secure_2026"
# استبدل بالرمز الدائم الذي ستستخرجه من ميتـا
WHATSAPP_TOKEN = "ضع_الرمز_الدائم_هنا" 
PHONE_NUMBER_ID = "1190456080809834"

def send_whatsapp_message(to_phone, message_body):
    """دالة لإرسال رد عبر واتساب"""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "text": {"body": message_body}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

@webhook_bp.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        # التحقق من ميتـا
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return 'Forbidden', 403

    elif request.method == 'POST':
        # استقبال رسائل واتساب
        data = request.get_json()
        
        try:
            # التحقق من وجود رسالة
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message_info = data['entry'][0]['changes'][0]['value']['messages'][0]
                sender_phone = message_info['from']
                message_text = message_info['text']['body']
                
                print(f"Received message from {sender_phone}: {message_text}")
                
                # إرسال رد تلقائي
                send_whatsapp_message(sender_phone, "أهلاً بك يا هندسة، لقد استلمت رسالتك بنجاح!")
        
        except (KeyError, IndexError):
            pass # تجاهل الأحداث التي لا تحتوي على رسائل نصية

        return 'OK', 200
