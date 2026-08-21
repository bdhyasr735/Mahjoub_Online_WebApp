# coding: utf-8
# 📂 apps/whatsapp_service/whatsapp_api.py

import os
import json
import requests
from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# إنشاء Blueprint لمسارات الواتساب
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

# جلب المتغيرات
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mahjoub_secure_webhook_token")
VERSION = os.getenv("VERSION", "v20.0")
BASE_URL = "https://graph.facebook.com"

def get_db():
    """Helper to get db instance safely from main app"""
    try:
        from app import db
        return db
    except ImportError:
        return None

# ==========================================
# 1. مسار الـ Webhook (مع الحفظ في قاعدة البيانات)
# ==========================================
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.get_json() or {}
    db = get_db()
    phone_id = PHONE_NUMBER_ID or 'system'

    try:
        # حفظ الحدث الخام للتدقيق (استخدام المسار العام الجديد للنماذج)
        if db:
            from apps.models.whatsapp_models import WhatsAppWebhookEvent, WhatsAppMessageLog, WhatsAppCustomerContact
            raw_event = WhatsAppWebhookEvent(
                event_type="incoming_payload",
                payload=data,
                processed=True
            )
            db.session.add(raw_event)
            db.session.commit()

        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages')
                
                if messages:
                    for msg in messages:
                        sender = msg.get('from')
                        msg_type = msg.get('type', 'text')
                        
                        if msg_type == 'text':
                            text = msg.get('text', {}).get('body', '')
                        else:
                            text = f'[{msg_type} attachment]'
                            
                        wamid = msg.get('id')
                        
                        # جلب اسم العميل من ملف البروفايل إن وجد
                        contacts_list = value.get('contacts', [])
                        customer_name = "عميل محجوب"
                        if contacts_list:
                            customer_name = contacts_list[0].get('profile', {}).get('name', 'عميل محجوب')

                        if db:
                            # تسجيل الرسالة الواردة
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

                            # تحديث أو إنشاء جهة اتصال العميل
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
                                    unread_count=1
                                )
                                db.session.add(new_contact)

                            db.session.commit()

    except Exception as e:
        print(f"❌ [Webhook Processing Error]: {str(e)}")
        if db:
            db.session.rollback()

    return jsonify({'status': 'success'}), 200

# ==========================================
# 2. مسارات جلب المحادثات والرسائل للوحة التحكم
# ==========================================
@whatsapp_bp.route('/chats', methods=['GET'])
def get_whatsapp_chats():
    db = get_db()
    if not db:
        return jsonify({"status": "error", "message": "Database unavailable"}), 500
    try:
        from apps.models.whatsapp_models import WhatsAppCustomerContact
        contacts = db.session.query(WhatsAppCustomerContact).order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
        chats_list = [{
            "phone": c.phone,
            "name": c.name or "عميل محجوب",
            "last_message": c.last_message or "",
            "last_timestamp": c.last_timestamp.strftime('%H:%M') if c.last_timestamp else "",
            "unread_count": c.unread_count or 0
        } for c in contacts]
        
        return jsonify({
            "status": "success",
            "chats": chats_list
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@whatsapp_bp.route('/messages/<phone_number>', methods=['GET'])
def get_chat_messages(phone_number):
    db = get_db()
    if not db:
        return jsonify({"status": "error", "message": "Database unavailable"}), 500
    try:
        from apps.models.whatsapp_models import WhatsAppMessageLog
        messages = db.session.query(WhatsAppMessageLog).filter(
            (WhatsAppMessageLog.sender_number == phone_number) | (WhatsAppMessageLog.recipient_number == phone_number)
        ).order_by(WhatsAppMessageLog.id.asc()).all()

        messages_list = [{
            "id": m.id,
            "direction": m.direction,
            "content": m.content,
            "timestamp": m.timestamp.strftime('%Y-%m-%d %H:%M') if m.timestamp else '',
            "status": m.status
        } for m in messages]

        return jsonify({
            "status": "success",
            "phone": phone_number,
            "messages": messages_list
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# 3. دالة إرسال الرسالة النصية المباشرة
# ==========================================
def send_text_message(to_number, message_body):
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_body}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()

# ==========================================
# 4. مسار اختبار الإرسال
# ==========================================
@whatsapp_bp.route('/send-send-test', methods=['GET'])
def test_send_message():
    target_phone = "967779077746"
    message_content = "مرحباً علي محجوب! تم الربط بنجاح مع سيرفر محجوب أونلاين. 🚀"
    
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        return jsonify({"status": "error", "message": "بيانات الاعتماد مفقودة"}), 400

    status, response_data = send_text_message(target_phone, message_content)
    
    return jsonify({
        "status_code": status,
        "meta_response": response_data,
        "note": "إذا فشل الإرسال، تأكد أنك أرسلت رسالة من هاتفك لرقم البوت أولاً لفتح نافذة المحادثة."
    })

# ==========================================
# 5. مسار إرسال الرسالة من لوحة التحكم (Dashboard API)
# ==========================================
@whatsapp_bp.route('/send-message', methods=['POST'])
def send_dashboard_message():
    db = get_db()
    data = request.get_json() or {}
    recipient_phone = data.get('phone')
    message_content = data.get('message')

    if not recipient_phone or not message_content:
        return jsonify({"status": "error", "message": "رقم الهاتف ونَص الرسالة مطلوبان"}), 400

    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        return jsonify({"status": "error", "message": "بيانات اعتماد واتساب مفقودة في الخادم"}), 500

    try:
        status_code, meta_response = send_text_message(recipient_phone, message_content)

        if status_code in [200, 201]:
            if db:
                from apps.models.whatsapp_models import WhatsAppMessageLog, WhatsAppCustomerContact
                
                wamid = None
                try:
                    wamid = meta_response.get('messages', [{}])[0].get('id')
                except Exception:
                    pass

                log_entry = WhatsAppMessageLog(
                    wamid=wamid,
                    direction='outbound',
                    sender_number=PHONE_NUMBER_ID,
                    recipient_number=recipient_phone,
                    customer_name="مشرف النظام",
                    message_type='text',
                    content=message_content,
                    status='sent'
                )
                db.session.add(log_entry)

                contact = db.session.query(WhatsAppCustomerContact).filter_by(phone=recipient_phone).first()
                if contact:
                    contact.last_message = f"أنت: {message_content}"
                    contact.last_timestamp = datetime.utcnow()
                
                db.session.commit()

            return jsonify({"status": "success", "message": "تم إرسال الرسالة بنجاح", "meta": meta_response}), 200
        else:
            return jsonify({"status": "error", "message": "فشل الإرسال من قبل ميتا", "meta": meta_response}), status_code

    except Exception as e:
        if db:
            db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# 6. دالة إرسال الفاتورة
# ==========================================
def send_invoice_whatsapp(to_number, order_id, total_price):
    url = f"{BASE_URL}/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "type": "template",
        "to": to_number,
        "template": {
            "name": "order_invoice", 
            "language": {"code": "ar"},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": str(order_id)},
                    {"type": "text", "text": str(total_price)}
                ]
            }]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()