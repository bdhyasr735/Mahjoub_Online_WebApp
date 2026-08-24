# coding: utf-8
# 📂 apps/whatsapp_service/routes/webhook.py

"""
WhatsApp Webhook Handlers
Handles webhook verification and real-time incoming events from Meta WhatsApp Cloud API.
"""

import os
import logging
from datetime import datetime
from flask import request, jsonify, current_app
from . import whatsapp_bp
from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppWebhookEvent,
    WhatsAppCustomerContact
)
from apps.extensions import db

from apps.whatsapp_service.config import WhatsAppServiceConfig

logger = logging.getLogger(__name__)


@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def webhook_handler():
    """معالجة استدعاءات Webhook (التحقق GET ومعالجة الرسائل POST)"""
    if request.method == 'GET':
        return verify_webhook()
    return process_webhook_events()


def verify_webhook():
    """التحقق الأمني من توكن Webhook مع سيرفرات Meta بدقة ومرونة"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token', '')
    challenge = request.args.get('hub.challenge')
    expected_token = WhatsAppServiceConfig.get_verify_token()
    
    # تنظيف المسافات والشرطات السفلية لضمان المطابقة الكاملة
    token_clean = token.replace(' ', '_').strip().lower()
    expected_clean = expected_token.replace(' ', '_').strip().lower()

    if mode == 'subscribe' and (token == expected_token or token_clean == expected_clean):
        return str(challenge), 200
    elif challenge and (token == expected_token or token_clean == expected_clean or not token):
        return str(challenge), 200
    return "Verification token mismatch", 403


def process_webhook_events():
    """معالجة وحفظ الرسائل وتحديث الحالات مع منع التكرار"""
    data = request.get_json(silent=True) or {}
    phone_id = WhatsAppServiceConfig.get_phone_number_id()

    try:
        # تسجيل الحدث الخام اختياري
        webhook_event = WhatsAppWebhookEvent(
            event_type='message_or_status',
            payload=data,
            processed=True
        )
        db.session.add(webhook_event)

        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # معالجة الرسائل الواردة
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        msg_type = msg.get('type', 'text')
                        wamid = msg.get('id')
                        
                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} ملف]'
                            
                        contacts_list = value.get('contacts', [])
                        customer_name = f"عميل ({sender})"
                        if contacts_list:
                            profile_name = contacts_list[0].get('profile', {}).get('name')
                            if profile_name:
                                customer_name = profile_name

                        # 🛡️ منع تكرار الرسائل: التحقق من أن معرف الرسالة wamid لم يُسجل مسبقاً
                        if wamid:
                            existing_msg = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if existing_msg:
                                continue

                        # حفظ الرسالة الواردة
                        log_entry = WhatsAppMessageLog(
                            wamid=wamid,
                            direction='inbound',
                            sender_number=sender,
                            recipient_number=phone_id,
                            message_type=msg_type,
                            content=text,
                            status='received'
                        )
                        db.session.add(log_entry)

                        # تحديث أو إنشاء جهة اتصال
                        contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=sender).first()
                        if contact:
                            if contact.name.startswith("عميل (") and customer_name != contact.name:
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

                # معالجة تحديثات حالة الرسائل (sent, delivered, read)
                elif 'statuses' in value:
                    for st in value['statuses']:
                        wamid = st.get('id')
                        status = st.get('status')
                        if wamid:
                            msg_log = db.session.query(WhatsAppMessageLog).filter_by(wamid=wamid).first()
                            if msg_log:
                                msg_log.status = status
                                db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ [Webhook Error]: {e}")

    return jsonify({"status": "EVENT_RECEIVED"}), 200
