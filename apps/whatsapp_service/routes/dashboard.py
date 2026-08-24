# coding: utf-8
"""
WhatsApp Webhook Handler
Handles incoming messages and verification requests from Meta Cloud API.
"""

from flask import request, jsonify
from datetime import datetime
from . import whatsapp_bp
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db
import os

# رمز التحقق المتفق عليه مع ميتا (يمكن قراءته من الإعدادات أو متغيرات البيئة)
WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_whatsapp_webhook():
    """التحقق من الويب هوك مع منصة ميتا (Handshake)"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED: تم التحقق من الويب هوك بنجاح عبر ميتا")
            return challenge, 200
        else:
            return jsonify({"error": "Forbidden"}), 403
    return jsonify({"error": "Bad Request"}), 400


@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_whatsapp_webhook():
    """استقبال الرسائل والإشعارات الواردة من واتساب وتخزينها فوراً"""
    try:
        data = request.get_json()
        
        # التأكد من أن الإشعار يخص واتساب
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages')
                    
                    if messages:
                        for message in messages:
                            phone_number = message.get('from')  # رقم مرسل الرسالة
                            msg_id = message.get('id')
                            timestamp = message.get('timestamp')
                            
                            # استخراج نص الرسالة (سواء كانت نصية أو نوع آخر)
                            msg_body = ""
                            msg_type = message.get('type')
                            if msg_type == 'text':
                                msg_body = message.get('text', {}).get('body', '')
                            else:
                                msg_body = f"[{msg_type} message]"
                                
                            # استخراج اسم المرسل إن وجد في الـ contacts
                            profile_name = "عميل واتساب"
                            contacts_info = value.get('contacts', [])
                            if contacts_info:
                                profile_name = contacts_info[0].get('profile', {}).get('name', 'عميل واتساب')

                            # 1. البحث عن العميل أو إنشاء سجل جديد له تلقائياً
                            contact = db.session.query(WhatsAppCustomerContact).filter_by(phone_number=phone_number).first()
                            
                            if not contact:
                                contact = WhatsAppCustomerContact(
                                    phone_number=phone_number,
                                    name=profile_name,
                                    last_message=msg_body,
                                    last_timestamp=datetime.fromtimestamp(int(timestamp)) if timestamp else db.func.current_timestamp()
                                )
                                db.session.add(contact)
                            else:
                                contact.name = profile_name if profile_name != "عميل واتساب" else contact.name
                                contact.last_message = msg_body
                                contact.last_timestamp = datetime.fromtimestamp(int(timestamp)) if timestamp else db.func.current_timestamp()
                            
                            db.session.commit()

                            # 2. تسجيل الرسالة في جدول سجلات المحادثات/الرسائل
                            new_log = WhatsAppMessageLog(
                                contact_id=contact.id,
                                message_id=msg_id,
                                direction='inbound',  # رسالة واردة
                                message_type=msg_type,
                                body=msg_body,
                                status='received'
                            )
                            db.session.add(new_log)
                            db.session.commit()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error handling webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
