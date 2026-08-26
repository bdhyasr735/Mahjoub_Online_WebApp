# apps/whatsapp_service/routes.py
from flask import Blueprint, request, jsonify, render_template
from .service import WhatsAppService

whatsapp_bp = Blueprint('whatsapp', __name__)
whatsapp_service = WhatsAppService()

# 1. مسار التحقق من الـ Webhook مع ميتا (Meta Verification)
@whatsapp_bp.route('/api/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == whatsapp_service.verify_token:
        return challenge, 200
    return "Verification failed", 403

# 2. مسار استقبال رسائل العملاء وأحداث التسليم (Webhook Inbound)
@whatsapp_bp.route('/api/whatsapp/webhook', methods=['POST'])
def handle_webhook_event():
    data = request.get_json()
    # التحقق من صحة وتوقيع الرسالة
    # استدعاء الخدمة لمعالجة الرسالة
    whatsapp_service.process_incoming_payload(data)
    return jsonify({"status": "received"}), 200

# 3. مسار عرض لوحة التحكم والقوالب التي جهزناها
@whatsapp_bp.route('/admin/whatsapp/dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin/dashboard.html')
