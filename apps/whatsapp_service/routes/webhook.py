# coding: utf-8
# 📂 apps/whatsapp_service/routes/webhook.py

import os
import logging
from datetime import datetime
from flask import request, jsonify, current_app

from apps.models.whatsapp_models import (
    WhatsAppMessageLog,
    WhatsAppCustomerContact
)
from apps.extensions import db
from . import whatsapp_bp

logger = logging.getLogger(__name__)

def get_verify_token():
    try:
        return current_app.config.get('WHATSAPP_VERIFY_TOKEN') or os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')
    except RuntimeError:
        return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')


@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('/webhook-admin', methods=['GET', 'POST'])
@whatsapp_bp.route('/admin/whatsapp/webhook', methods=['GET', 'POST'])
def direct_webhook():
    if request.method == 'GET':
        return verify_webhook()
    
    # استخدام force=True لتجنب أي رفض من Flask بسبب اختلاف ترويسة Content-Type ومنع خطأ 400
    data = request.get_json(silent=True, force=True) or {}
    
    if not data:
        return jsonify({"status": "ok", "note": "empty_payload_received"}), 200
        
    return handle_webhook_data(data)


def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    verify_token = get_verify_token()
    if mode == 'subscribe' and token == verify_token:
        return str(challenge), 200
    elif challenge and (token == verify_token or not token):
        return str(challenge), 200
    return "Verification token mismatch", 403


def handle_webhook_data(data):
    phone_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID') or os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'system')

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # معالجة الرسائل الواردة
                if 'messages' in value:
                    for msg in value['messages']:
                        sender = msg.get('from')
                        if not sender:
                            continue
                            
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

                        # التحقق من عدم تكرار حفظ نفس الرسالة
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
                            contact.name = customer_name if not contact.name or contact.name.startswith("عميل (") else contact.name
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

                # معالجة تحديثات حالة الرسائل (تم التسليم، تمت القراءة)
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
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 200

    return jsonify({"status": "EVENT_RECEIVED"}), 200
