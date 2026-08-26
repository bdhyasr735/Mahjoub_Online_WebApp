# app.py (أو main.py)
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from apps.whatsapp_service.service import WhatsAppService

app = Flask(__name__)

# إنشاء نسخة من الخدمة التي كتبتها
wa_service = WhatsAppService()

# ==========================================================
# 1. مسار التحقق (Handshake GET Request) - يطلبه Meta عند التسجيل
# ==========================================================
@app.route('/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == wa_service.verify_token:
        print("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        return jsonify({"error": "Verification failed"}), 403

# ==========================================================
# 2. مسار استقبال الرسائل (POST Request) - المرسل من Meta
# ==========================================================
@app.route('/whatsapp/webhook', methods=['POST'])
def receive_webhook():
    # قراءة البيانات الواردة
    data = request.get_json()
    
    # (اختياري) التحقق من التوقيع الأمني إذا كان لديك App Secret
    raw_payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not wa_service.verify_webhook_signature(raw_payload, signature):
        return jsonify({"error": "Invalid signature"}), 403
    
    try:
        # استدعاء دالة المعالجة من الكود الذي أرسلته
        wa_service.process_incoming_payload(data)
        # يجب إرجاع 200 دائماً حتى لا تعيد Meta إرسال الرسالة
        return jsonify({"status": "EVENT_RECEIVED"}), 200
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ==========================================================
# 3. مسارات إضافية للوحة التحكم (كما في الصور)
# ==========================================================
@app.route('/admin/whatsapp/dashboard', methods=['GET'])
def admin_dashboard():
    return jsonify({
        "contacts": wa_service.get_all_contacts(),
        "messages": wa_service.messages_db, 
        "config": wa_service.get_current_config()
    })

@app.route('/admin/whatsapp/webhook-logs', methods=['GET'])
def admin_webhook_logs():
    return jsonify(wa_service.get_webhook_logs())

@app.route('/admin/whatsapp/config', methods=['POST'])
def update_config():
    new_config = request.get_json()
    wa_service.update_config(new_config)
    return jsonify({"success": True, "config": wa_service.get_current_config()})

if __name__ == '__main__':
    # تشغيل الخادم (استخدم ngrok أو رابط HTTPS حقيقي لتجربة Meta)
    # تأكد من أن متغيرات البيئة (Access Token, App Secret...) موجودة
    app.run(host='0.0.0.0', port=5000, debug=True)
