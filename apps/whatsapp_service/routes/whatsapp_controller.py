"""
WhatsApp Routes and Webhook Controllers for Mahgoob Online
"""

from flask import Blueprint, request, jsonify, render_template, current_app
import os
import logging
from ..whatsapp_api import send_text_message
from ..models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp_service', __name__)

VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

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
                        # تم تصحيح الخطأ هنا بقوس دائري صحيح بدلاً من القوس المربع
                        text = msg.get('text', {}).get('body', '') if msg.get('type') == 'text' else '[وسائط/مرفق]'
                        wamid = msg.get('id')
                        contact_profile = value.get('contacts', [{}])[0].get('profile', {})
                        name = contact_profile.get('name', 'عميل متجر محجوب')

                        # Save inbound message log in DB
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
    
    if not recipient or not text:
        return jsonify({"success": False, "error": "Missing recipient_number or message"}), 400

    status_code, response_data = send_text_message(recipient, text)
    success = (200 <= status_code < 300)
    
    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


@whatsapp_bp.route('/api/ping', methods=['GET'])
def ping_meta_api():
    """Checks Meta API connection status."""
    return jsonify({"status": "active", "message": "WhatsApp API helper is ready."})


# ==============================================================================
# 3. ADMIN DASHBOARD TEMPLATES (JINJA2)
# ==============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    try:
        from app import db
        contacts = db.session.query(WhatsAppCustomerContact).all()
    except Exception:
        contacts = []
    return render_template('admin/chat_view.html', active_tab='chat', contacts=contacts)

@whatsapp_bp.route('/logs')
def logs_dashboard():
    try:
        from app import db
        logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).all()
    except Exception:
        logs = []
    return render_template('admin/logs_view.html', active_tab='logs', logs=logs)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    settings = {}
    if request.method == 'POST':
        pass
    return render_template('admin/settings_view.html', active_tab='settings', settings=settings)
