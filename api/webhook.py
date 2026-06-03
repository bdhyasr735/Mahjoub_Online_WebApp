from flask import Blueprint, request, jsonify

# إنشاء Blueprint لتنظيم الـ API
webhook_bp = Blueprint('webhook', __name__)

VERIFY_TOKEN = "Mahjoob_WhatsApp_Secure_2026"

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
        
        # هنا سنضع كود معالجة الرسائل لاحقاً
        # مثلاً: إرسال رد تلقائي أو حفظ في قاعدة البيانات
        print(f"Received message: {data}")
        
        return 'OK', 200
