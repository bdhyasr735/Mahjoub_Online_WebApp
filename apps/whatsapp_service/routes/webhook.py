# coding: utf-8
"""
WhatsApp Webhook Handler (Integrated with WhatsApp API structure)
"""

from flask import request, jsonify
from datetime import datetime
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db
import os

WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
@whatsapp_bp.route('', methods=['GET', 'POST'])
def whatsapp_webhook_handler():
    """معالجة التحقق واستقبال الرسائل الواردة وتخزينها"""
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
                return challenge, 200
            else:
                return jsonify({"error": "Forbidden"}), 403
        return jsonify({"error": "Bad Request"}), 400

    else:
        try:
            data = request.get_json()
            
            if data and data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        messages = value.get('messages')
                        
                        if messages:
                            for message in messages:
                                phone_number = message.get('from')  # رقم المرسل
                                msg_id = message.get('id')
                                timestamp = message.get('timestamp')
                                
                                # محتوى الرسالة
                                msg_body = ""
                                msg_type = message.get('type')
                                if msg_type == 'text':
                                    msg_body = message.get('text', {}).get('body', '')
                                else:
                                    msg_body = f"[{msg_type} message]"
                                    
                                # اسم المرسل من الـ payload إن وجد
                                profile_name = f"عميل ({phone_number})"
                                contacts_info = value.get('contacts', [])
                                if contacts_info:
                                    profile_name = contacts_info[0].get('profile', {}).get('name', profile_name)

                                msg_time = datetime.fromtimestamp(int(timestamp)) if timestamp else datetime.utcnow()

                                # 1. البحث عن جهة الاتصال باستخدام حقل phone (المطابق لـ whatsapp_api.py)
                                contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=phone_number).first()
                                
                                if not contact:
                                    contact = WhatsAppCustomerContact(
                                        phone=phone_number,
                                        name=profile_name,
                                        last_message=msg_body,
                                        last_timestamp=msg_time,
                                        unread_count=1
                                    )
                                    db.session.add(contact)
                                else:
                                    contact.last_message = msg_body
                                    contact.last_timestamp = msg_time
                                    # زيادة عدد الرسائل غير المقروءة إن لم تكن المحادثة مفتوحة
                                    try:
                                        contact.unread_count = (contact.unread_count or 0) + 1
                                    except:
                                        pass
                                
                                db.session.commit()

                                # 2. حفظ سجل الرسالة الواردة (Inbound Log) مطابراً لـ WhatsAppMessageLog
                                new_log = WhatsAppMessageLog(
                                    wamid=msg_id,
                                    direction='inbound',
                                    sender_number=phone_number,
                                    recipient_number=value.get('metadata', {}).get('phone_number_id', ''),
                                    content=msg_body,
                                    status='received'
                                )
                                db.session.add(new_log)
                                db.session.commit()

            return jsonify({"status": "success"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error handling webhook: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
