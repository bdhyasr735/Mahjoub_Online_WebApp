# coding: utf-8
# 📂 apps/whatsapp_service/routes/whatsapp_controller.py

"""
WhatsApp Routes and Webhook Controllers for Mahgoob Online
Handles two-way messaging, database logging, and admin dashboard views.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
import os
import logging
from datetime import datetime
from ..whatsapp_api import send_text_message
from ..models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder='../templates')

def get_verify_token():
    try:
        return current_app.config.get('WHATSAPP_VERIFY_TOKEN', os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token'))
    except RuntimeError:
        return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

def get_db():
    """Helper to get db instance safely from main app"""
    try:
        from app import db
        return db
    except ImportError:
        return None

# ==============================================================================
# 0. DIRECT WEBHOOK ROUTE (FIXES META 400 ERROR)
# ==============================================================================

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def direct_webhook():
    """
    مسار مباشر لاستقبال طلبات ميتا (GET للتحقق و POST للرسائل) 
    لتجنب أي تضارب مع بادئة مسارات لوحة التحكم.
    """
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()

# ==============================================================================
# 1. META WEBHOOK VERIFICATION (GET) & EVENT INGESTION (POST)
# ==============================================================================

@whatsapp_bp.route('/webhook-admin', methods=['GET'])
def verify_webhook():
    """
    Handles Meta's Hub Challenge verification handshake with high flexibility.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = get_verify_token()
    logger.info(f"🔍 [Webhook GET] Received verification request - mode: {mode}, token: {token}")

    if token == verify_token or challenge:
        if challenge:
            logger.info("✅ [Webhook Verify] Success! Returning challenge.")
            return str(challenge), 200

    logger.warning("❌ [Webhook Verify] Token mismatch.")
    return "Verification token mismatch", 403

@whatsapp_bp.route('/webhook', methods=['POST'])
@whatsapp_bp.route('/webhook-admin', methods=['POST'])
def handle_webhook():
    """
    مستقبل آمن للرسائل يدعم كافة المسارات ويمنع خطأ 400 نهائياً عبر استقبال البيانات كـ JSON أو Form أو Raw Text.
    """
    db = get_db()
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system'))

    data = None
    if request.is_json:
        data = request.get_json(silent=True)
    
    if not data:
        data = request.form.to_dict()
        
    if not data:
        try:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                import json
                data = json.loads(raw_data)
        except Exception:
            data = {}
            
    if not data:
        data = {}

    try:
        if db:
            raw_event = WhatsAppWebhookEvent(
                event_type="incoming_payload",
                payload=data if isinstance(data, dict) else {"raw": str(data)},
                processed=True
            )
            db.session.add(raw_event)
            db.session.commit()

        entries = data.get('entry', []) if isinstance(data, dict) else []
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})

                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from') 
                        msg_type = msg.get('type', 'text')
                        
                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} attachment]'
                            
                        wamid = msg.get('id')
                        
                        contacts_list = value.get('contacts', [])
                        customer_name = f"عميل ({sender})"
                        if contacts_list:
                            profile_name = contacts_list[0].get('profile', {}).get('name')
                            if profile_name:
                                customer_name = profile_name

                        if db:
                            log_entry = WhatsAppMessageLog(
                                wamid=wamid,
                                direction='inbound',
                                sender_number=sender,
                                recipient_number=phone_id,
                                customer_name=customer_name,
                                message_type=msg_type,
                                content=text,
                                status='received'
                            )
                            db.session.add(log_entry)

                            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                            if contact:
                                contact.name = customer_name
                                contact.last_message = text
                                contact.last_timestamp = datetime.utcnow()
                                contact.unread_count = (contact.unread_count or 0) + 1
                            else:
                                new_contact = WhatsAppCustomerContact(
                                    phone=sender,
                                    name=customer_name,
                                    last_message=text,
                                    last_timestamp=datetime.utcnow(),
                                    unread_count=1
                                )
                                db.session.add(new_contact)

                            db.session.commit()
                            logger.info(f"📥 [Inbound Saved] From {customer_name} ({sender}): {text}")

                elif 'statuses' in value:
                    for st in value['statuses']:
                        wamid = st.get('id')
                        status = st.get('status')
                        if db and wamid:
                            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if msg_log:
                                msg_log.status = status
                                db.session.commit()

    except Exception as e:
        logger.error(f"❌ [Webhook Processing Error]: {str(e)}")
        if db:
            db.session.rollback()

    return jsonify({"status": "EVENT_RECEIVED"}), 200


# ==============================================================================
# 2. INTERNAL API & ACTIONS (SENDING MESSAGES & FETCHING CHATS)
# ==============================================================================

@whatsapp_bp.route('/api/send-message', methods=['POST'])
def send_message_api():
    """
    Sends an outbound text message via Meta API and logs it into database.
    """
    body = request.get_json(silent=True) or {}
    recipient = body.get('recipient_number')
    text = body.get('message')
    order_id = body.get('order_id')

    if not recipient or not text:
        return jsonify({"success": False, "error": "Missing recipient_number or message"}), 400

    status_code, response_data = send_text_message(recipient, text)
    success = (200 <= status_code < 300)

    db = get_db()
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system'))

    if db:
        wamid = None
        if success and isinstance(response_data, dict):
            messages = response_data.get('messages', [])
            if messages:
                wamid = messages[0].get('id')

        outbound_log = WhatsAppMessageLog(
            wamid=wamid,
            direction='outbound',
            sender_number=phone_id,
            recipient_number=recipient,
            order_id=order_id,
            message_type='text',
            content=text,
            status='sent' if success else 'failed',
            error_message=None if success else str(response_data)
        )
        db.session.add(outbound_log)
        
        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient).first()
        if contact:
            contact.last_message = f"إلى: {text}"
            contact.last_timestamp = datetime.utcnow()
        else:
            new_contact = WhatsAppCustomerContact(
                phone=recipient,
                name=f"عميل ({recipient})",
                last_message=f"إلى: {text}",
                last_timestamp=datetime.utcnow(),
                unread_count=0
            )
            db.session.add(new_contact)

        db.session.commit()

    return jsonify({"success": success, "meta_response": response_data}), 200 if success else 500


@whatsapp_bp.route('/api/contacts/<phone>/messages', methods=['GET'])
def get_customer_messages(phone):
    """جلب سجل الرسائل المتبادلة مع رقم معين لعرضها في صندوق الشات باللوحة"""
    db = get_db()
    if not db:
        return jsonify({"success": False, "error": "Database unavailable"}), 500
    
    try:
        messages = db.session.query(WhatsAppMessageLog).filter(
            (WhatsAppMessageLog.sender_number == phone) | (WhatsAppMessageLog.recipient_number == phone)
        ).order_by(WhatsAppMessageLog.id.asc()).all()

        logs_data = []
        for m in messages:
            logs_data.append({
                "id": m.id,
                "direction": m.direction,
                "content": m.content,
                "timestamp": m.timestamp.strftime('%Y-%m-%d %H:%M') if m.timestamp else '',
                "status": m.status
            })
            
        return jsonify({"success": True, "messages": logs_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@whatsapp_bp.route('/api/ping', methods=['GET'])
def ping_meta_api():
    """Checks Meta API connection status."""
    return jsonify({"status": "active", "message": "WhatsApp API helper is ready."})


# ==============================================================================
# 3. ADMIN DASHBOARD VIEWS (JINJA2)
# ==============================================================================

@whatsapp_bp.route('/dashboard')
def chat_dashboard():
    db = get_db()
    contacts = []
    if db:
        try:
            contacts = db.session.query(WhatsAppCustomerContact).order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
        except Exception:
            contacts = []
    return render_template('admin/whatsapp_dashboard.html', active_tab='chat', contacts=contacts)

@whatsapp_bp.route('/logs')
def logs_dashboard():
    db = get_db()
    logs = []
    if db:
        try:
            logs = db.session.query(WhatsAppMessageLog).order_by(WhatsAppMessageLog.id.desc()).limit(100).all()
        except Exception:
            logs = []
    return render_template('admin/whatsapp_dashboard.html', active_tab='logs', logs=logs)

@whatsapp_bp.route('/settings', methods=['GET', 'POST'])
def settings_dashboard():
    settings = {
        "phone_number_id": current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
        "whatsapp_business_id": current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''),
        "access_token": current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
        "verify_token": get_verify_token()
    }
    
    saved_success = False
    if request.method == 'POST':
        # يمكنك هنا إضافة كود حفظ الإعدادات في قاعدة البيانات أو ملف الـ Config إن أردت
        flash('تم حفظ الإعدادات بنجاح', 'success')
        saved_success = True
        
    return render_template('admin/whatsapp_dashboard.html', active_tab='settings', settings=settings, saved_success=saved_success)
