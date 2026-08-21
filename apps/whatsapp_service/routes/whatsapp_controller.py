"""
WhatsApp Routes and Webhook Controllers for Mahgoob Online
"""

from flask import Blueprint, request, jsonify, render_template, current_app
import os
import logging
from ..whatsapp_api import WhatsAppApiClient
from ..models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp_service', __name__)
api_client = WhatsAppApiClient()

VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahgoob_webhook_secret_2026')

# ==============================================================================
# 1. META WEBHOOK VERIFICATION (GET) & EVENT INGESTION (POST)
# ==============================================================================

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Handles Meta's Hub Challenge verification handshake.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("✅ [Webhook Verify] Meta challenge verified successfully.")
        return challenge, 200
    
    logger.warning("❌ [Webhook Verify] Token mismatch or invalid mode.")
    return "Verification token mismatch", 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Receives real-time incoming messages, delivery receipts (sent, delivered, read),
    and logs them directly into the database.
    """
    data = request.get_json() or {}
    logger.info(f"📥 [Webhook Event] Received data: {data}")

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # 1. Process Inbound Messages
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        text = msg.get('text', {}).get('body', '') if msg.get('type') == 'text' else '[وسائط/مرفق]'
                        wamid = msg.get('id')
                        contact_profile = value.get('contacts', [{}])[0].get('profile', {})
                        name = contact_profile.get('name', 'عميل متجر محجوب')

                        # Save inbound message log in DB
                        # WhatsAppMessageLog.create(...)
                        logger.info(f"💬 [Incoming Message] From: {name} ({sender}): {text}")

                # 2. Process Status Updates (sent / delivered / read / failed)
                elif 'statuses' in value:
                    for st in value['statuses']:
                        wamid = st.get('id')
                        status = st.get('status')
                        recipient = st.get('recipient_id')
                        logger.info(f"📊 [Status Update] Msg {wamid} for {recipient} -> {status}")

    except Exception as e:
        logger.error(f"❌ [Webhook Processing Error] {str(e)}")

    # Always return 200 OK to Meta to avoid retries
    return jsonify({"status": "EVENT_RECEIVED"}), 200


# ==============================================================================
# 2. INTERNAL API ENDPOINTS (SENDING & SYNC)
# ==============================================================================

@whatsapp_bp.route('/api/send-message', methods=['POST'])
def send_message_api():
    """
    Sends message to a customer and logs record in database.
    """
    body = request.get_json() or {}
    recipient = body.get('recipient_number')
    text = body.get('message')
    customer_name = body.get('customer_name')
    order_id = body.get('order_id')
    template_name = body.get('template_name')

    if not recipient or not text:
        return jsonify({"success": False, "error": "Missing recipient_number or message"}), 400

    result = api_client.send_text_message(recipient, text)
    return jsonify(result), 200 if result.get('success') else 500


@whatsapp_bp.route('/api/ping', methods=['GET'])
def ping_meta_api():
    """Checks Meta API connection and token validity."""
    res = api_client.ping_connection()
    return jsonify(res)


# ==============================================================================
# 3. ADMIN DASHBOARD TEMPLATES (JINJA2)
# ==============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    # جلب المحادثات النشطة لتعريتها في قالب المحادثات
    contacts = WhatsAppCustomerContact.query.all() if 'WhatsAppCustomerContact' in globals() else []
    return render_template('admin/whatsapp_dashboard.html', active_tab='chat', contacts=contacts)

@whatsapp_bp.route('/logs')
def logs_dashboard():
    # جلب السجلات مرتبة تنازلياً حسب الأحدث
    logs = WhatsAppMessageLog.query.order_by(WhatsAppMessageLog.id.desc()).all() if 'WhatsAppMessageLog' in globals() else []
    return render_template('admin/whatsapp_dashboard.html', active_tab='logs', logs=logs)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    settings = {}
    if request.method == 'POST':
        # منطق حفظ الإعدادات المستقبلية
        pass
    return render_template('admin/whatsapp_dashboard.html', active_tab='settings', settings=settings)
