# coding: utf-8
# 📂 apps/whatsapp_service/routes/webhook.py

"""
WhatsApp Webhook Handler
Receives real-time events from Meta WhatsApp Cloud API:
- New incoming messages
- Message status updates (sent, delivered, read)
- Other business events
"""

import json
import logging
from datetime import datetime
from flask import request, jsonify, current_app
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppWebhookEvent, WhatsAppCustomerContact
from apps.extensions import db

logger = logging.getLogger(__name__)


# =========================================================
# 1. نقطة نهاية Webhook الموحدة (GET + POST)
# =========================================================
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def direct_webhook():
    """
    نقطة نهاية Webhook الرئيسية.
    - GET: التحقق من صحة الرابط (Handshake مع ميتا).
    - POST: استقبال الأحداث الفعلية (رسائل، تحديثات حالة، إلخ).
    """
    if request.method == 'GET':
        return verify_webhook()
    return handle_webhook()


# =========================================================
# 2. التحقق من Webhook (GET) – Handshake مع ميتا
# =========================================================
def verify_webhook():
    """
    معالجة طلب التحقق من ميتا (GET).
    يجب أن يعيد نفس قيمة hub.challenge إذا تطابق الرمز.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # جلب رمز التحقق من الإعدادات
    verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

    # التحقق من صحة الطلب
    if mode == 'subscribe' and token == verify_token:
        logger.info("✅ Webhook verified successfully with Meta")
        return str(challenge), 200
    elif challenge and (token == verify_token or not token):
        # بعض عملاء ميتا يرسلون challenge فقط
        return str(challenge), 200

    logger.warning(f"⚠️ Webhook verification failed: mode={mode}, token={token[:5] if token else 'None'}...")
    return "Verification token mismatch", 403


# =========================================================
# 3. معالجة الأحداث الواردة (POST) – جوهر النظام
# =========================================================
def handle_webhook():
    """
    معالجة الأحداث القادمة من ميتا (POST).
    - رسائل جديدة (messages)
    - تحديثات حالة (statuses)
    """
    # قراءة البيانات الخام
    raw_data = request.get_data(as_text=True)
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or 'system'

    # محاولة تحويل JSON
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
        logger.warning("⚠️ Empty webhook payload received")
        return jsonify({"status": "OK"}), 200

    # تسجيل الحدث الخام في قاعدة البيانات (للتدقيق)
    try:
        raw_event = WhatsAppWebhookEvent(
            event_type="incoming_payload",
            payload=data,
            processed=False
        )
        db.session.add(raw_event)
        db.session.commit()
    except Exception as e:
        logger.error(f"❌ Failed to log webhook event: {e}")
        db.session.rollback()

    # معالجة الأحداث
    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # ----- 3.1 معالجة الرسائل الواردة -----
                if 'messages' in value:
                    process_incoming_messages(value, phone_id)

                # ----- 3.2 معالجة تحديثات الحالة -----
                if 'statuses' in value:
                    process_status_updates(value)

        # تحديث حالة معالجة الحدث في السجل
        raw_event.processed = True
        db.session.commit()

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        db.session.rollback()
        return jsonify({"status": "ERROR", "message": str(e)}), 500

    return jsonify({"status": "EVENT_RECEIVED"}), 200


# =========================================================
# 4. معالجة الرسائل الواردة (مصححة ومحسنة)
# =========================================================
def process_incoming_messages(value, phone_id):
    """
    معالجة الرسائل الواردة من العملاء.
    - حفظ الرسالة في قاعدة البيانات.
    - تحديث أو إنشاء جهة اتصال.
    """
    for msg in value.get('messages', []):
        try:
            sender = msg.get('from')
            msg_type = msg.get('type', 'text')
            wamid = msg.get('id')
            timestamp = msg.get('timestamp')

            # استخراج محتوى الرسالة حسب النوع
            if msg_type == 'text':
                text = msg.get('text', {}).get('body', '')
            elif msg_type == 'image':
                text = "📷 [صورة]"
            elif msg_type == 'video':
                text = "🎬 [فيديو]"
            elif msg_type == 'document':
                text = "📄 [مستند]"
            elif msg_type == 'audio':
                text = "🎵 [صوت]"
            else:
                text = f"[{msg_type}]"

            # استخراج اسم العميل من بيانات ميتا
            contacts_list = value.get('contacts', [])
            customer_name = f"عميل ({sender})"
            whatsapp_profile_name = None
            if contacts_list:
                profile_name = contacts_list[0].get('profile', {}).get('name')
                if profile_name:
                    customer_name = profile_name
                    whatsapp_profile_name = profile_name

            # التحقق من عدم تكرار الرسالة (باستخدام WAMID)
            existing = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if existing:
                logger.debug(f"⏭️ Duplicate message {wamid}, skipping")
                continue

            # تحويل التوقيت بشكل آمن
            try:
                msg_timestamp = datetime.fromtimestamp(int(timestamp)) if timestamp else datetime.utcnow()
            except (ValueError, TypeError):
                msg_timestamp = datetime.utcnow()

            # 1. حفظ الرسالة في قاعدة البيانات
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

            # 2. تحديث أو إنشاء جهة اتصال
            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
            if contact:
                # تحديث الاسم إذا كان افتراضياً أو مختلفاً
                if contact.name.startswith("عميل (") or contact.name != customer_name:
                    contact.name = customer_name
                if whatsapp_profile_name and contact.whatsapp_profile_name != whatsapp_profile_name:
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
            logger.info(f"📩 New message from {sender} ({customer_name}): {text[:30]}...")

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to save message from {sender}: {e}")
            continue


# =========================================================
# 5. معالجة تحديثات حالة الرسائل (مصححة)
# =========================================================
def process_status_updates(value):
    """
    معالجة تحديثات حالة الرسائل (مرسلة، مسلمة، مقروءة، فشلت).
    """
    for st in value.get('statuses', []):
        try:
            wamid = st.get('id')
            status = st.get('status')
            recipient = st.get('recipient_id')
            timestamp = st.get('timestamp')

            if not wamid:
                continue

            # تحويل التوقيت بشكل آمن
            try:
                status_timestamp = datetime.fromtimestamp(int(timestamp)) if timestamp else None
            except (ValueError, TypeError):
                status_timestamp = None

            # تحديث حالة الرسالة في قاعدة البيانات
            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
            if msg_log:
                msg_log.status = status
                if status_timestamp:
                    msg_log.timestamp = status_timestamp
                db.session.commit()
                logger.debug(f"📨 Status update: {wamid} → {status}")
            else:
                logger.warning(f"⚠️ Status update for unknown message: {wamid}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to update status for {wamid}: {e}")
            continue
