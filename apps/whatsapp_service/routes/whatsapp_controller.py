# coding: utf-8
# 📂 apps/whatsapp_service/routes/whatsapp_controller.py

"""
WhatsApp Routes and Webhook Controllers for Mahgoob Online
"""

from flask import Blueprint, request, jsonify, render_template, current_app
import os
import logging
# استيراد الدوال مباشرة من ملف whatsapp_api
from ..whatsapp_api import send_text_message, send_invoice_whatsapp, VERIFY_TOKEN

logger = logging.getLogger(__name__)

# نضع الـ prefix هنا ليتكفل ببادئة الإدارة والخدمة تلقائياً
whatsapp_bp = Blueprint('whatsapp_service', __name__, url_prefix='/admin/whatsapp')

# ==============================================================================
# 1. META WEBHOOK VERIFICATION (GET) & EVENT INGESTION (POST)
# ==============================================================================

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
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
    data = request.get_json() or {}
    logger.info(f"📥 [Webhook Event] Received data: {data}")

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        text = msg.get('text', {}).get('body', '') if msg.get('type') == 'text' else '[وسائط/مرفق]'
                        logger.info(f"💬 [Incoming Message] From: {sender}: {text}")
                elif 'statuses' in value:
                    for st in value['statuses']:
                        logger.info(f"📊 [Status Update] -> {st.get('status')}")
    except Exception as e:
        logger.error(f"❌ [Webhook Processing Error] {str(e)}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200


# ==============================================================================
# 2. INTERNAL API ENDPOINTS
# ==============================================================================

@whatsapp_bp.route('/api/send-message', methods=['POST'])
def send_message_api():
    body = request.get_json() or {}
    recipient = body.get('recipient_number')
    text = body.get('message')

    if not recipient or not text:
        return jsonify({"success": False, "error": "Missing recipient_number or message"}), 400

    status_code, resp_data = send_text_message(recipient, text)
    
    success = (200 <= status_code < 300)
    return jsonify({"success": success, "status_code": status_code, "response": resp_data}), 200 if success else 500


@whatsapp_bp.route('/api/ping', methods=['GET'])
def ping_meta_api():
    # فحص بسيط للاتصال بناءً على توفر المفاتيح
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
    token = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
    
    if phone_id and token:
        return jsonify({"status": "connected", "message": "Meta Cloud API credentials configured."})
    return jsonify({"status": "disconnected", "message": "Missing API credentials."}), 400


# ==============================================================================
# 3. ADMIN DASHBOARD TEMPLATES (JINJA2)
# ==============================================================================

@whatsapp_bp.route('/dashboard', methods=['GET'])
def chat_dashboard():
    """لوحة محادثات العملاء - العرض السيادي"""
    mock_contacts = [] 
    return render_template(
        'admin/chat_view.html', 
        active_tab='chat',
        contacts=mock_contacts
    )

@whatsapp_bp.route('/logs', methods=['GET'])
def logs_dashboard():
    """لوحة سجل الرسائل"""
    return render_template('admin/whatsapp_logs.html', active_tab='logs')

@whatsapp_bp.route('/settings', methods=['GET'])
def settings_dashboard():
    """لوحة إعدادات Meta Cloud API"""
    return render_template('admin/whatsapp_settings.html', active_tab='settings')
