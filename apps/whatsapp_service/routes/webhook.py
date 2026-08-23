# coding: utf-8
# 📂 apps/whatsapp_service/routes/webhook.py

"""
WhatsApp Webhook Handler
Receives real-time events from Meta WhatsApp Cloud API:
- New incoming messages & button clicks
- Message status updates (sent, delivered, read, failed)
- Raw event logging
"""

import json
import logging
from datetime import datetime
from flask import request, jsonify, current_app
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact
from apps.extensions import db, csrf

logger = logging.getLogger(__name__)


# =========================================================
# 1. نقطة نهاية Webhook الموحدة (مع إعفاء CSRF)
# =========================================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
@csrf.exempt  # إعفاء Webhook Meta من حماية CSRF
def direct_webhook():
    """
    نقطة نهاية Webhook الرئيسية.
    - GET: التحقق من صحة الرابط (Handshake مع ميتا).
    - POST: استقبال الأحداث الفعلية (رسائل، أزرار، تحديثات حالة).
    """
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()


# =========================================================
# 2. التحقق من Webhook (GET) – Handshake مع ميتا
# =========================================================
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

    if mode == 'subscribe' and token == verify_token:
        logger.info("✅ Webhook verified successfully with Meta")
        return str(challenge), 200
    elif challenge and (token == verify_token or not token):
        return str(challenge), 200

    logger.warning(f"⚠️ Webhook verification failed: mode={mode}, token={token[:5] if token else 'None'}...")
    return "Verification token mismatch", 403


# =========================================================
# 3. معالجة الأحداث الواردة (POST)
# =========================================================
def handle_webhook():
    raw_data = request.get_data(as_text=True)
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or 'system'

    data = None
    try:
        if request.is_json:
            data = request.get_json(silent=True)
        if not data and raw_data:
            data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        return jsonify({"status": "ERROR", "message": "Invalid JSON"}), 400

    if not data:
        return jsonify({"status": "OK"}), 200

    # 1. تسجيل الحدث الخام في قاعدة البيانات
    event_id = None
    try:
        raw_event = WhatsAppWebhookEvent(
            event_type="incoming_payload",
            payload=data,
            processed=False
        )
        db.session.add(raw_event)
        db.session.commit()
        event_id = raw_event.id
    except Exception as e:
        logger.error(f"❌ Failed to log raw webhook event: {e}")
        db.session.rollback()

    # 2. معالجة الرسائل والتحديثات
    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # معالجة الرسائل والردود على القوالب
                if 'messages' in value:
                    process_incoming_messages(value, phone_id)

                # معالجة تحديثات حالة الإرسال
                if 'statuses' in value:
                    process_status_updates(value)

        # تحديث حالة معالجة الحدث الخام
        if event_id:
            db.session.query(WhatsAppWebhookEvent).filter_by(id=event_id).update({"processed": True})
            db.session.commit()

    except Exception as e:
        logger.error(f"❌ Error processing webhook content: {e}")
        db.session.rollback()

    # الإرجاع الدائم لـ 200 OK لضمان عدم توقف Webhook لدى Meta
    return jsonify({"status": "EVENT_RECEIVED"}), 200


# =========================================================
# 4. معالجة الرسائل الواردة وتفاعلات القوالب
# =========================================================
def process_incoming_messages(value, phone_id):
    for msg in value.get('messages', []):
        try:
            sender = msg.get('from')
            msg_type = msg.get('type', 'text')
            wamid = msg.get('id')
            timestamp = msg.get('timestamp')

            # استخراج محتوى الرسالة بحسب النوع (بما فيها تفاعلات القوالب والأزرار)
            text = ""
            if msg_type == 'text':
                text = msg.get('text', {}).get('body', '')
            elif msg_type == 'interactive':
                interactive = msg.get('interactive', {})
                i_type = interactive.get('type')
                if i_type == 'button_reply':
                    text = f"🔘 {interactive.get('button_reply', {}).get('title', '')}"
                elif i_type == 'list_reply':
                    text = f"📋 {interactive.get('list_reply', {}).get('title', '')}"
                else:
                    text = "[تفاعل أزرار]"
            elif msg_type == 'button':
                text = f"🔘 {msg.get('button', {}).get('text', '')}"
            elif msg_type == 'image':
                caption = msg.get('image', {}).get('caption', '')
                text = f"📷 [صورة]{' - ' + caption if caption else ''}"
            elif msg_type == 'video':
                caption = msg.get('video', {}).get('caption', '')
                text = f"🎬 [فيديو]{' - ' + caption if caption else ''}"
            elif msg_type == 'document':
                caption = msg.get('document', {}).get('caption', '')
                text = f"📄 [مستند]{' - ' + caption if caption else ''}"
            elif msg_type == 'audio':
                text = "🎵 [رسالة صوتية]"
            elif msg_type == 'location':
                text = "📍 [موقع جغرافي]"
            else:
                text = f"[{msg_type}]"

            # استخراج اسم العميل من البروفايل
            contacts_list = value.get('contacts', [])
            customer_name = f"عميل ({sender})"
            whatsapp_profile_name = None
            if contacts_list:
                profile_name = contacts_list[0].get('profile', {}).get('name')
                if profile_name:
                    customer_name = profile_name
                    whatsapp_profile_name = profile_name

            # منع تكرار المعالجة بنفس الـ WAMID
            existing = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if existing:
                continue

            try:
                msg_timestamp = datetime.fromtimestamp(int(timestamp)) if timestamp else datetime.utcnow()
            except (ValueError, TypeError):
                msg_timestamp = datetime.utcnow()

            # 1. حفظ سجل الرسالة الواردة
            log_entry = WhatsAppMessageLog(
                wamid=wamid,
                direction='inbound',
                sender_number=sender,
                recipient_number=phone_id,
                message_type=msg_type,
                content=text,
                status='received',
                timestamp=msg_timestamp
            )
            db.session.add(log_entry)

            # 2. تحديث أو إنشاء جهة الاتصال
            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
            if contact:
                if contact.name.startswith("عميل (") or contact.name != customer_name:
                    contact.name = customer_name
                if whatsapp_profile_name:
                    contact.whatsapp_profile_name = whatsapp_profile_name
                contact.last_message = text
                contact.last_timestamp = datetime.utcnow()
                contact.unread_count = (contact.unread_count or 0) + 1
                contact.is_online = True
            else:
                new_contact = WhatsAppCustomerContact(
                    phone=sender,
                    name=customer_name,
                    whatsapp_profile_name=whatsapp_profile_name,
                    last_message=text,
                    last_timestamp=datetime.utcnow(),
                    unread_count=1,
                    is_online=True
                )
                db.session.add(new_contact)

            db.session.commit()
            logger.info(f"📩 Incoming message/button from {sender}: {text}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to process incoming message: {e}")


# =========================================================
# 5. معالجة تحديثات حالة الرسائل
# =========================================================
def process_status_updates(value):
    for st in value.get('statuses', []):
        try:
            wamid = st.get('id')
            status = st.get('status')
            timestamp = st.get('timestamp')

            if not wamid:
                continue

            try:
                status_timestamp = datetime.fromtimestamp(int(timestamp)) if timestamp else None
            except (ValueError, TypeError):
                status_timestamp = None

            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if msg_log:
                msg_log.status = status
                if status_timestamp:
                    msg_log.timestamp = status_timestamp
                db.session.commit()
                logger.debug(f"📨 Status update: {wamid} -> {status}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to update status for {wamid}: {e}")
